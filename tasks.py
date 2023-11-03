from invoke import task


@task
def rundev(ctx):
    ctx.run("uvicorn main:app --reload --host 0.0.0.0 --port 8000")
