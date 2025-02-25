import time
from functools import cached_property

from module.base.timer import Timer
from module.base.utils import _area_offset, crop, extract_letters, find_letter_area, float2str, point2str
from module.logger import logger
from module.ocr.ocr import Digit
from module.rookie_arena.assets import *
from module.ui.assets import ROOKIE_ARENA_CHECK
from module.ui.page import page_rookie_arena
from module.ui.ui import UI


class RookieArena(UI):
    @property
    def free_opportunity_remain(self) -> bool:
        result = FREE_OPPORTUNITY_CHECK.appear_on(self.device.image)
        logger.info(f'[Free opportunity remain] {result}')
        return result

    @property
    def competitor_power_list(self) -> list[int]:
        start_time = time.time()
        r = [i.get('area') for i in POWER_CHECK.match_several(self.device.image, threshold=0.66, static=False)]
        # 按照 upper 排序
        r.sort(key=lambda x: x[1])
        r = [_area_offset(i, (22, -10, 65, 8)) for i in r]

        r = [self.ocr_models.get('nikke').ocr(crop(crop(self.device.image, i), _area_offset(
            find_letter_area(extract_letters(crop(self.device.image, i), letter=(90, 93, 99)) < 128), (-2, -2, 3, 2))))
             for i in r]

        r = list(map(lambda x: int(x[0]['text']), r))
        logger.attr(name='%s %ss' % ('COMPETITOR_POWER_LIST', float2str(time.time() - start_time)),
                    text=str(r))

        return r

    @cached_property
    def own_power(self) -> int:
        area = _area_offset(OWN_POWER_CHECK.area, (20, -2, 70, 2))
        OWN_POWER = Digit([area], name='OWN_POWER', letter=(247, 247, 247), threshold=128)
        return int(OWN_POWER.ocr(self.device.image))

    @cached_property
    def button(self):
        return [(590, 710), (590, 840), (590, 980)]

    def start_competition(self, skip_first_screenshot=True):
        logger.hr('Start a competition')
        competitor = [index for index, i in enumerate(self.competitor_power_list) if i <= self.own_power]

        if not len(competitor):
            competitor.append(2)
            logger.warning("detected no competitor's power below own power")
            logger.warning('will choose the third competitor')

        confirm_timer = Timer(1, count=5).start()
        click_timer = Timer(0.3)
        click_timer_2 = Timer(5)

        already_start = False

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if not already_start \
                    and click_timer.reached() \
                    and click_timer_2.reached() \
                    and FREE_OPPORTUNITY_CHECK.appear_on(self.device.image):
                self.device.click_minitouch(*self.button[competitor[0]])
                logger.info(
                    'Click %s @ %s' % (point2str(*self.button[competitor[0]]), 'START_COMPETITION')
                )
                confirm_timer.reset()
                click_timer.reset()
                click_timer_2.reset()
                continue

            if not already_start \
                    and click_timer.reached() \
                    and self.appear_then_click(INTO_COMPETITION, offset=(30, 30), interval=5):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if not already_start \
                    and click_timer.reached() \
                    and self.appear(END_COMPETITION, offset=(30, 30), interval=5):
                logger.info(
                    'Click %s @ %s' % (point2str(100, 100), 'END_COMPETITION')
                )
                self.device.click_minitouch(100, 100)
                already_start = True
                confirm_timer.reset()
                click_timer.reset()
                continue

            if already_start and self.appear(ROOKIE_ARENA_CHECK, offset=(10, 10)) and confirm_timer.reached():
                break

        if self.free_opportunity_remain:
            return self.start_competition()

    def run(self):
        self.ui_ensure(page_rookie_arena, confirm_wait=2)
        if self.free_opportunity_remain:
            self.start_competition()
        else:
            logger.info('There are no free opportunities')
        self.config.task_delay(server_update=True)
