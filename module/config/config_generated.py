import datetime

# This file was automatically generated by module/config/config_updater.py.
# Don't modify it manually.


class GeneratedConfig:
    """
    Auto generated configuration
    """

    # Group `Scheduler`
    Scheduler_Enable = False
    Scheduler_NextRun = datetime.datetime(1989, 12, 27, 0, 0)
    Scheduler_Command = 'NKAS'
    Scheduler_SuccessInterval = 0
    Scheduler_FailureInterval = 120
    Scheduler_ServerUpdate = '04:00'

    # Group `Emulator`
    Emulator_Serial = 'auto'
    Emulator_PackageName = 'com_proximabeta_nikke'  # com_proximabeta_nikke, com_gamamobi_nikke
    Emulator_ScreenshotMethod = 'DroidCast'  # DroidCast
    Emulator_ControlMethod = 'minitouch'  # minitouch
    Emulator_AdbRestart = False

    # Group `Optimization`
    Optimization_WhenTaskQueueEmpty = 'goto_main'  # stay_there, goto_main, close_game

    # Group `Reward`
    Reward_CollectSocialPoint = True
    Reward_CollectSpecialArenaPoint = True

    # Group `Conversation`
    Conversation_WaitToCommunicate = None

    # Group `Area`
    Area_Difficulty = 'Level_1'  # Level_1, Level_2, Level_3, Level_4, Level_5
    Area_OnsetArea = 'A'  # A, B, C
    Area_EndingArea = 'A'  # A, B, C

    # Group `Overcome`
    Overcome_OnlyToCompleteDailyMission = False

    # Group `GeneralShop`
    GeneralShop_enable = True

    # Group `ArenaShop`
    ArenaShop_enable = False
    ArenaShop_priority = None

    # Group `RubbishShop`
    RubbishShop_priority = None

    # Group `Notification`
    Notification_WhenDailyTaskCompleted = False

    # Group `Event`
    Event_Event_Name = None
    Event_Complete_Event = False
    Event_Event = 'event_1'  # event_1
    Event_Part = 'story_1'  # story_1, story_2
    Event_Difficulty = 'normal'  # normal, hard

    # Group `Daily`
    Daily_EnhanceEquipment = False

    # Group `Storage`
    Storage_Storage = {}
