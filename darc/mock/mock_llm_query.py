mock_QADev_query = """```python
import pytest

def add_integers(a, b):
    if not (isinstance(a, int) and isinstance(b, int)):
        raise ValueError("Both inputs must be integers.")
    return a + b

# Test functions for pytest
def test_add_integers_with_integers():
    assert add_integers(3, 4) == 7

def test_add_integers_with_negative_integers():
    assert add_integers(-1, -2) == -3

def test_add_integers_with_zero():
    assert add_integers(0, 0) == 0

def test_add_integers_with_large_integers():
    assert add_integers(123456789, 987654321) == 1111111110

def test_add_integers_with_non_integer_first_argument():
    with pytest.raises(ValueError):
        add_integers("a", 1)

def test_add_integers_with_non_integer_second_argument():
    with pytest.raises(ValueError):
        add_integers(1, "b")

def test_add_integers_with_both_non_integer_arguments():
    with pytest.raises(ValueError):
        add_integers("a", "b")
```"""

mock_PM_query = """作为产品经理，如果团队需要创建一个整数加法函数，我的任务是确保这个功能满足用户的需求，
并且与开发团队沟通这个需求的具体细节。下面是我会采取的步骤：

1. **需求分析**:
   - 与用户沟通，了解他们需要整数加法函数的场景和用途。
   - 确定加法函数需要支持的整数范围（例如，是否需要支持负数，是否有最大整数限制等）。

2. **功能规格说明**:
   - 编写详细的功能需求文档，包括输入参数的类型、函数的预期行为以及输出结果的格式。
   - 确定函数是否需要处理异常情况，如非整数输入、超出范围的整数等。

3. **与开发团队沟通**:
   - 将功能需求文档与开发团队分享。
   - 讨论实现细节，确保开发团队完全理解需求。
   - 确认开发时间表和里程碑，确保按时交付。

4. **迭代计划**:
   - 制定产品的迭代计划，如果需要，可以先发布基础版本，之后根据用户反馈进行增强。
   - 确定优先级，决定哪些功能是核心功能，哪些可以稍后添加。

5. **跟踪和评估**:
   - 跟踪开发进度，确保项目按计划进行。
   - 定期与开发团队会面，解决开发中遇到的问题。
   - 准备测试计划，确保功能的正确性和性能。

6. **用户测试和反馈**:
   - 在功能开发完成后，组织用户测试。
   - 收集用户反馈，评估功能是否满足用户需求。

7. **产品改进**:
   - 根据用户反馈，与开发团队合作对功能进行调整和优化。
   - 更新文档和用户指南，确保用户能够理解和使用新功能。

8. **发布和宣传**:
   - 确保功能发布后有相应的宣传和用户教育材料。
   - 监控功能发布后的用户采用情况和反馈。

通过上述步骤，我作为产品经理将确保整数加法函数不仅能够满足用户的基本需求，而且具有良好的用户体验和可靠性。
同时，我还会确保产品的持续改进和优化，以适应市场和用户的变化需求。"""

mock_FeatureDev_query = """```python
def add_integers(a, b):
    if not (isinstance(a, int) and isinstance(b, int)):
        raise ValueError("Both inputs must be integers.")
    return a + b
```"""
