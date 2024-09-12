import pytest
from unittest.mock import mock_open, patch
from darc.agent.llm.proxy.query import get_system_prompt_with_uid, query_with_uid
import logging

@pytest.mark.skip("skip")
def test_get_system_prompt_with_uid():
    assert get_system_prompt_with_uid("35aac978-59dd-43cf-ac41-5cd1fcb02154") == "A Political Analyst specialized in El Salvador's political landscape."
    
    assert get_system_prompt_with_uid("e78c7ae2-8944-478b-882f-1d54a89a0da3") == "A legal advisor who understands the legal implications of incomplete or inaccurate project documentation"

def test_query_with_uid():
    question = "What is the capital of France?"
    uid = "35aac978-59dd-43cf-ac41-5cd1fcb02154"
    
    answer = query_with_uid(question, uid)
    assert answer is not None