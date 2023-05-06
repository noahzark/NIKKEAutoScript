from functools import cached_property

import cv2

from module.base.timer import Timer
from module.base.utils import _area_offset, crop, mask_area, extract_letters, find_letter_area, point2str, \
    find_center, save_image
from module.conversation._conversation import Nikke_list, Nikke_dialog
from module.conversation.assets import *
from module.exception import GamePageUnknownError
from module.handler.assets import CONFRIM_B, AUTO_CLICK_CHECK
from module.logger import logger
from module.ocr.ocr import DigitCounter
from module.ui.assets import CONVERSATION_CHECK, GOTO_BACK
from module.ui.page import page_conversation
from module.ui.ui import UI

OCR_OPPORTUNITY = DigitCounter(OCR_OPPORTUNITY, lang='cnocr', name='OCR_OPPORTUNITY', letter=(247, 247, 247),
                               threshold=128)


class ChooseNextNIKKETooLong(Exception):
    pass


class NoOpportunityRemain(Exception):
    pass


class ConversationQueueIsEmpty(Exception):
    pass


class Conversation(UI):
    visited = set()

    stuck_timer = Timer(60, count=0).start()
    confirm_timer = Timer(4, count=5).start()

    @cached_property
    def nikke_list(self):
        try:
            _ = self.config.Conversation_WaitToCommunicate.strip(' ').split(' ')
            logger.attr('NIKKE LIST', _)
            return _
        except AttributeError:
            logger.warning("There are no names included in the queue option")
            raise ConversationQueueIsEmpty

    def match(self, img, button: Button):
        button.ensure_template()
        res = cv2.matchTemplate(img, button.image, cv2.TM_CCOEFF_NORMED)
        _, similarity, _, upper_left = cv2.minMaxLoc(res)
        if similarity > 0.85:
            return True

    def name_after_process(self, text, img):
        if text:
            if '购物狂' in text:
                text = '冬日购物狂'
            elif '奇迹' in text:
                text = '奇迹仙女'
        else:
            logger.warning("cannot detect the current NIKKE's name")

        # TODO 奇迹仙女, 以及其他不好识别的NIKKE
        if self.match(img, RUPEE_WINTER_SHOPPER):
            text = '冬日购物狂'
        elif self.match(img, RUPEE):
            text = '露菲'
        elif self.match(img, D):
            text = 'D'
        if text not in self.visited:
            return text

    def get_next_target(self):
        if not self.opportunity:
            logger.attr('VISITED NIKKE LIST', self.visited)
            logger.warning('There are no opportunities remaining')
            raise NoOpportunityRemain

        elif self.stuck_timer.reached():
            logger.attr('VISITED NIKKE LIST', self.visited)
            logger.attr('stuck timer reached', self.stuck_timer.reached())
            logger.warning('Perhaps all selected NIKKE already had a conversation')
            raise ChooseNextNIKKETooLong
        # elif len(self.visited) == len(self.nikke_list):
        #     logger.attr('VISITED NIKKE LIST', self.visited)
        #     logger.warning('Perhaps all selected NIKKE already had a conversation')
        #     raise ChooseNextNIKKETooLong

        _ = FAVOURITE_CHECK.match(self.device.image, static=False)
        if _:
            area = FAVOURITE_CHECK._button_offset
            name_area = _area_offset(area, (18, 57, 220, -10))
            check_area = _area_offset(area, (520, 57, 645, 12))
            _img = crop(self.device.image, name_area)
            _img = extract_letters(_img, letter=(74, 73, 74))
            text_rect = find_letter_area(_img < 128)
            text_rect = _area_offset(text_rect, (-2, -2, 3, 2))
            _letters_img = crop(_img, text_rect)
            name = self.name_after_process(self.ocr(_letters_img, 'NIKKE_NAME'), _img)
            # save_image(_letters_img, './RUPEE.png')
            if not name:
                self.device.image = mask_area(self.device.image, area)
                return self.get_next_target()

            self.visited.add(name)
            # 咨询状态
            if CASE_CLOSED.match(crop(self.device.image, check_area), static=False):
                logger.warning('already had a conversation with current nikke')
                logger.warning("skip this nikke's conversation")
                self.device.image = mask_area(self.device.image, area)
                return self.get_next_target()

            r = [i.get('key') for i in Nikke_list if i.get('label') in name]

            if not len(r):
                logger.warning(f"don't support communication with {name}")
                logger.warning("skip this nikke's conversation")
                self.device.image = mask_area(self.device.image, area)
                return self.get_next_target()

            _ = list(filter(lambda x: x == name, self.nikke_list))

            if not len(_):
                logger.warning(f"{name} not included in the option")
                self.device.image = mask_area(self.device.image, area)
                return self.get_next_target()

            self.confirm_timer.reset()
            super().__setattr__('current', name)
            super().__setattr__('key', r[0])
            return

        self.device.screenshot()
        if not self.appear(CONVERSATION_CHECK, offset=(10, 10)):
            logger.warning('Perhaps the current page was changed by a human or certain error')
            logger.critical("Please switch current page into 'PAGE_CONVERSATION'")
            raise GamePageUnknownError

        elif self.confirm_timer.reached():
            logger.attr('VISITED NIKKE LIST', self.visited)
            logger.attr('confirm timer reached', self.confirm_timer.reached())
            logger.warning('Perhaps all selected NIKKE already had a conversation')
            raise ChooseNextNIKKETooLong

        self.device.swipe((360, 1000), (360, 960), handle_control_check=False)
        self.device.sleep(1.3)
        self.device.screenshot()
        self.get_next_target()

    def communicate(self):
        logger.hr('Start a conversation')
        self.get_next_target()
        if self.ensure_in_detail():
            self.ensure_wait_to_answer()
            self.answer()

    def ensure_in_detail(self, skip_first_screenshot=True):
        logger.hr('into detailed information', 3)
        confirm_timer = Timer(1, count=1).start()
        click_timer = Timer(1.6)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() \
                    and not DETAIL_CHECK.match(self.device.image):
                self.device.click(FAVOURITE_CHECK)
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.appear(DETAIL_CHECK, offset=(10, 10)) and confirm_timer.reached():
                break

        if RANK_MAX_CHECK.match(self.device.image):
            logger.warning('current nikke already achieved max rank')
            logger.warning("skip this nikke's conversation")
            confirm_timer.reset()
            click_timer.reset()
            skip_first_screenshot = True
            while 1:
                if skip_first_screenshot:
                    skip_first_screenshot = False
                else:
                    self.device.screenshot()

                if click_timer.reached() and not CONVERSATION_CHECK.match(self.device.image):
                    self.device.click(GOTO_BACK)
                    confirm_timer.reset()
                    click_timer.reset()
                    continue

                if self.appear(CONVERSATION_CHECK, offset=(10, 10)) and confirm_timer.reached():
                    self.device.image = mask_area(self.device.image, FAVOURITE_CHECK._button_offset)
                    return self.communicate()

        return True

    def ensure_wait_to_answer(self, skip_first_screenshot=True):
        logger.hr(f'have a conversation with {self.current}', 3)
        click_timer = Timer(0.3)

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(COMMUNICATE, offset=(30, 30), interval=3):
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear_then_click(CONFRIM_B, offset=(30, 30), interval=3):
                click_timer.reset()
                continue

            if self.appear(ANSWER_CHECK, offset=(1, 1), static=False):
                self.device.sleep(0.5)
                break

            if click_timer.reached() and self.appear(AUTO_CLICK_CHECK, offset=(30, 30), interval=0.3):
                self.device.click_minitouch(100, 100)
                logger.info(
                    'Click %s @ %s' % (point2str(100, 100), 'WAIT_TO_ANSWER')
                )
                click_timer.reset()
                continue

    def answer(self, skip_first_screenshot=True):
        correct_answer = Nikke_dialog.get(self.key)
        click_timer = Timer(0.5)

        answer_a_area = (82, 817, 640, 900)
        answer_b_area = (82, 920, 640, 1000)

        answer_a = self.ocr(extract_letters(crop(self.device.image, answer_a_area), letter=(247, 243, 247)),
                            label='OCR_ANSWER_A')
        answer_b = self.ocr(extract_letters(crop(self.device.image, answer_b_area), letter=(247, 243, 247)),
                            label='OCR_ANSWER_B')

        def cannot_decide():
            import time
            logger.warning('cannot decide the correct answer,will choose Answer A')
            self.device.sleep(1)
            save_image(self.device.screenshot(), f'./cannot_decide_answer_{time.time()}.png')
            self.device.click_minitouch(*find_center(answer_a_area))

        def get_similarity(sentences, target, threshold=0.8):
            import difflib
            if target is None:
                return 0, ''
            max_ratio = 0
            max_sentence = ''
            for sentence in sentences:
                ratio = difflib.SequenceMatcher(None, sentence, target).quick_ratio()
                if ratio > max_ratio:
                    max_ratio = ratio
                    max_sentence = sentence
            if max_ratio < threshold:
                return 0, ''
            return max_ratio, max_sentence

        try:
            if len(list(filter(lambda x: list(x) and x in answer_a, correct_answer))):
                logger.info('Answer A seems to be the correct one')
                self.device.click_minitouch(*find_center(answer_a_area))
            elif len(list(filter(lambda x: list(x) and x in answer_b, correct_answer))):
                logger.info('Answer B seems to be the correct one')
                self.device.click_minitouch(*find_center(answer_b_area))
            else:
                ratio_a, similar_a = get_similarity(correct_answer, answer_a)
                ratio_b, similar_b = get_similarity(correct_answer, answer_b)
                if ratio_a > ratio_b >= 0:
                    logger.info('Answer A seems to be the correct one similar to %s', similar_a)
                    self.device.click_minitouch(*find_center(answer_a_area))
                elif ratio_b > ratio_a >= 0:
                    logger.info('Answer B seems to be the correct one similar to %s', similar_b)
                    self.device.click_minitouch(*find_center(answer_b_area))
                else:
                    cannot_decide()
        except TypeError:
            cannot_decide()

        self.opportunity -= 1
        self.stuck_timer.reset()

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self.appear(DETAIL_CHECK, offset=(30, 30), static=False) \
                    or self.appear(RANK_INCREASE_CHECK, offset=(30, 30), static=False):
                break

            # if click_timer.reached() and self.appear(AUTO_CLICK_CHECK, offset=(30, 30), interval=0.3):
            if click_timer.reached():
                self.device.click_minitouch(*find_center(answer_a_area))
                logger.info(
                    'Click %s @ %s' % (point2str(*find_center(answer_a_area)), 'ANSWER')
                )
                click_timer.reset()
                continue

        self.ensure_back()

    def ensure_back(self, skip_first_screenshot=True):
        confirm_timer = Timer(1, count=2).start()
        click_timer = Timer(0.3)

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(RANK_INCREASE_COMFIRM, offset=(10, 10), interval=3,
                                                                static=False):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() \
                    and not self.appear(CONVERSATION_CHECK, offset=(10, 10)) \
                    and self.appear_then_click(GOTO_BACK, offset=(10, 10), interval=3):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.appear(CONVERSATION_CHECK, offset=(10, 10)) and confirm_timer.reached():
                break

        return self.communicate()

    def ensure_opportunity_remain(self):
        super().__setattr__('opportunity', int(OCR_OPPORTUNITY.ocr(self.device.image)[0]))
        return self.opportunity

    def run(self):
        self.ui_ensure(page_conversation, confirm_wait=3)
        if self.ensure_opportunity_remain():
            try:
                self.communicate()
            except ChooseNextNIKKETooLong as e:
                logger.error(e)
            except NoOpportunityRemain as e:
                logger.error(e)
            except ConversationQueueIsEmpty as e:
                logger.error(e)
        else:
            logger.info('There are no opportunities remaining')
        self.config.task_delay(server_update=True)


def _find_letter_area(image, area):
    _img = crop(image, area)
    _img = extract_letters(_img, letter=(247, 243, 247))
    text_rect = find_letter_area(_img < 128)
    text_rect = _area_offset(text_rect, (-2, -2, 3, 2))
    return crop(crop(image, area), text_rect)
