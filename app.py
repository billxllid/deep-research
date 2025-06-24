from fastapi import FastAPI


def app():
    server = FastAPI()
    print("APP start ...")

if __name__ == "__main__":
    app()