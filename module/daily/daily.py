from module.base.timer import Timer
from module.base.utils import mask_area, point2str
from module.common.enum.webui import ICON
from module.daily.assets import *
from module.logger import logger
from module.ui.assets import DAILY_CHECK, INVENTORY_CHECK
from module.ui.page import page_daily, page_inventory
from module.ui.ui import UI


class NoItemsError(Exception):
    pass


class Daily(UI):
    def receive(self, skip_first_screenshot=True):
        logger.hr('Reward receive', 2)
        confirm_timer = Timer(3, count=3).start()
        click_timer = Timer(0.3)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()
                self.device.image = mask_area(self.device.image, COMPLETED_CHECK.button)

            if click_timer.reached() and self.appear_then_click(COMPLETED_CHECK, offset=(5, 5), interval=6,
                                                                threshold=0.8, static=False):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear_then_click(RECEIVE, offset=(5, 5), interval=1,
                                                                static=False):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.handle_reward(1):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.appear(DAILY_CHECK, offset=(10, 10)) and confirm_timer.reached():
                self.device.screenshot()
                if self.appear(COMPLETED_CHECK, offset=(5, 5), threshold=0.8, static=False):
                    skip_first_screenshot = True
                    continue
                break

    def toast(self):
        from winotify import Notification
        toast = Notification(app_id="NKAS",
                             title="NKAS",
                             msg="任务已全部完成！",
                             icon=ICON.Helm_Circle,
                             duration='long')

        toast.show()

    # enhance equipment
    def enhance_equipment(self, skip_first_screenshot=True):
        logger.hr('ENHANCE EQUIPMENT', 2)
        confirm_timer = Timer(1, count=1).start()
        click_timer = Timer(0.3)
        click_timer_2 = Timer(3)

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(GOTO_EQUIPMENT_LIST, offset=(30, 30), interval=3):
                click_timer.reset()
                continue

            if self.appear(NO_ITEMS, offset=(30, 30)):
                raise NoItemsError

            if self.appear(INVENTORY_CHECK, offset=(30, 30)) and not self.appear(GOTO_EQUIPMENT_LIST, offset=(
                    30, 30)) and confirm_timer.reached():
                break

        skip_first_screenshot = True
        confirm_timer.limit = 4
        confirm_timer.count = 3
        confirm_timer.reset()
        click_timer.reset()
        click_timer_2.reset()
        flag = False

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() \
                    and self.appear(INVENTORY_CHECK, offset=(30, 30)) \
                    and self.appear_then_click(RANDOM_EQUIPMENT, offset=(5, 5), interval=3, static=False):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear_then_click(ENHANCE, offset=(5, 5), interval=3):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if not flag and click_timer_2.reached() \
                    and (self.appear_then_click(NORMAL_MATERIALS, offset=(5, 5), interval=3)
                         or self.appear_then_click(ADVANCED_MATERIALS, offset=(5, 5), interval=3)):
                confirm_timer.reset()
                click_timer_2.reset()
                continue

            if click_timer.reached() and self.appear_then_click(ENHANCE_CONFIRM, offset=(5, 5), interval=3):
                flag = True
                confirm_timer.reset()
                click_timer.reset()
                continue

            if confirm_timer.reached():
                if flag:
                    logger.info('already enhanced a random equipment in the inventory')
                else:
                    logger.warning('Not enough materials to enhance a equipment')
                self.ensure_back()
                return

    def ensure_back(self, skip_first_screenshot=True):
        confirm_timer = Timer(1, count=1).start()
        click_timer = Timer(0.3)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and not self.appear(INVENTORY_CHECK, offset=(30, 30)):
                self.device.click_minitouch(300, 100)
                logger.info(
                    'Click %s @ %s' % (point2str(300, 100), 'BACK')
                )
                click_timer.reset()
                continue

            if self.appear(INVENTORY_CHECK, offset=(10, 10)) and confirm_timer.reached():
                break

    def run(self):
        try:
            if self.config.Daily_EnhanceEquipment:
                self.ui_ensure(page_inventory)
                self.enhance_equipment()
        except NoItemsError:
            logger.warning('No equipments in the inventory')
            self.ensure_back()
        self.ui_ensure(page_daily)
        self.receive()
        if self.config.Notification_WhenDailyTaskCompleted:
            self.toast()
        self.config.task_delay(server_update=True)
