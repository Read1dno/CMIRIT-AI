class Settings:
    # standart YOLO models:
    #TARGET_CLASSES = {
    #    2: 'car',
    #    5: 'bus',
    #    7: 'truck',
    #    1: 'bicycle',
    #    3: 'motorcycle',
    #    0: 'person',
    #}
    # train model in cher
    TARGET_CLASSES = {
        0: 'person',
        1: 'bicycle',
        2: 'car',
        3: 'motorcycle',
        4: 'bus',
        5: 'truck'
    }

    COLORS = {
        0: (0, 255, 0),
        1: (255, 0, 0),
        2: (0, 0, 255),
        3: (255, 255, 0),
        5: (255, 0, 255),
        7: (0, 255, 255),
    }

    MAX_TRAJECTORY_LENGTH = 30
    DISTANCE_THRESHOLD = 20