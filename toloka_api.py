import requests
import time
import pandas as pd

class TolokaProcessingApi:
    def __init__(self, toloka_token):
        self.toloka_token = toloka_token
        self.headers = headers = {"Authorization": "OAuth " + toloka_token}

    def create_toloka_project(self, project_params):
        req = requests.post("https://toloka.yandex.ru/api/v1/projects", headers=self.headers, json=project_params)
        assert (req.ok)
        new_project_id = req.json()['id']
        print("New project was created. New project id: ", new_project_id)
        print("https://toloka.yandex.ru/requester/project/{}".format(new_project_id))
        return new_project_id

    def create_toloka_pool(self, project_id, pool_params):
        pool_params['project_id'] = str(project_id)
        req = requests.post("https://toloka.yandex.ru/api/v1/pools", headers=self.headers, json=pool_params)
        assert (req.ok)
        new_pool_id = req.json()['id']
        print("New pool was created. New pool id: ", new_pool_id)
        return new_pool_id

    def clone_toloka_pool(self, pool_id):
        req = requests.post("https://toloka.yandex.ru/api/v1/pools/{}/clone".format(pool_id), headers=self.headers)
        assert (req.ok)
        operation_id = req.json()['id']
        time.sleep(10)
        operation_status = requests.get("https://toloka.yandex.ru/api/v1/operations/{}".format(operation_id),
                                        headers=self.headers).json()

        assert (operation_status['status'] == 'SUCCESS')

        new_pool_id = operation_status['details']['pool_id']
        print("Pool was cloned. New pool was created. New pool id: ", new_pool_id)
        print("https://toloka.yandex.ru/requester/pool/{}".format(new_pool_id))
        return new_pool_id

    def upload_toloka_tasks(self, tasks):
        req = requests.post("https://toloka.yandex.ru/api/v1/task-suites?allow_defaults=true",
                            headers=self.headers, json=tasks)
        if not req.ok:
            print(req.text)
        assert (req.ok)

    def run_toloka_pool(self, pool_id):
        req = requests.post("https://toloka.yandex.ru/api/v1/pools/{}/open".format(pool_id), headers=self.headers)
        assert (req.ok)
        print("Pool {} was started".format(pool_id))

    def print_toloka_pool_link(self, pool_id):
        print("https://toloka.yandex.ru/requester/pool/{}".format(pool_id))

    def get_pool_params(self, pool_id):
        req = requests.get("https://toloka.yandex.ru//api/v1/pools/{}".format(pool_id), headers=self.headers)
        assert req.ok
        return req.json()

    def update_pool_params(self, pool_id, pool_params):
        req = requests.put("https://toloka.yandex.ru//api/v1/pools/{}".format(pool_id), headers=self.headers,
                           json=pool_params)
        assert req.ok

    def get_pool_completed_tasks(self, pool_id):
        req = requests.get("https://toloka.yandex.ru/api/v1/assignments?pool_id={}&limit=10000".format(pool_id),
                           headers=self.headers)
        completed_items = req.json()["items"]
        # return completed_items
        all_tasks = []
        all_solutions = []
        for i in completed_items:
            if i.get('solutions') is not None:
                tasks = i.get('tasks', [[]])
                tasks = list(map(lambda x: x['input_values'], tasks))
                all_tasks += tasks

                task_solutions = i.get('solutions', [[]])
                task_solutions = list(map(lambda x: x.get("output_values", [[]]), task_solutions))
                all_solutions += task_solutions

        df = pd.merge(pd.DataFrame(all_tasks), pd.DataFrame(all_solutions), left_index=True, right_index=True)
        return df
