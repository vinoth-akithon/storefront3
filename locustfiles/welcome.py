from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def say_hello(self):
        self.client.get("/playground/index/")
