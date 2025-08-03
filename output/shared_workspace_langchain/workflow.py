def main_workflow(context):
    """主工作流"""
    # STEP: generate_math_utils
    result1 = generate_math_utils()
    # STEP: run_tests
    result2 = run_tests()
    # STEP: review_code
    result3 = review_code()
    return {result1, result2, result3}

def generate_math_utils():
    task = "Create a Python class named MathUtils in /home/guci/aiProjects/mda/output/shared_workspace_langchain/math_utils.py.  The class should contain methods for addition, subtraction, multiplication, division, and power.  Include error handling for division by zero."
    response = default_api.code_generator(task=task)
    if response['status'] == 'success':
        return { 'status': 'success', 'file_path': '/home/guci/aiProjects/mda/output/shared_workspace_langchain/math_utils.py'}
    else:
        return { 'status': 'failure', 'error': response['error']}

def run_tests():
    task = "Run tests on /home/guci/aiProjects/mda/output/shared_workspace_langchain/math_utils.py to verify that all methods work correctly."
    response = default_api.code_runner(task=task)
    if response['status'] == 'success':
        return { 'status': 'success'}
    else:
        return { 'status': 'failure', 'error': response['error']}

def review_code():
    task = "Review the code quality of /home/guci/aiProjects/mda/output/shared_workspace_langchain/math_utils.py and provide a score (1-10). Follow the principle of concise output plus document references."
    response = default_api.code_reviewer(task=task)
    if response['status'] == 'success':
        return { 'status': 'success', 'score': response['score']}
    else:
        return { 'status': 'failure', 'error': response['error']}
