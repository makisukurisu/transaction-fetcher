import logging

db_logger = logging.getLogger("db")

db_logger.setLevel(logging.INFO)
db_logger.propagate = False
db_logger.addHandler(logging.StreamHandler())
db_logger.handlers[0].setFormatter(
    logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
)
db_logger.handlers[0].setLevel(logging.INFO)


main_logger = logging.getLogger("main")
main_logger.setLevel(logging.INFO)
main_logger.propagate = False
main_logger.addHandler(logging.StreamHandler())
main_logger.handlers[0].setFormatter(
    logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
)
main_logger.handlers[0].setLevel(logging.INFO)
