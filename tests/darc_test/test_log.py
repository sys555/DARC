import logging
logger = logging.getLogger(__name__)

def test_case():
    logger.info("断言1==1")
    assert 1==1