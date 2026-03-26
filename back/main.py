from fastapi import FastAPI
import drivers, disabled, cars, drive_requests, shop_requests, reviews

app = FastAPI(
    title="Mobility CRUD API",
    description="CRUD API for drivers, disabled users, cars, requests and reviews",
    version="1.0.0",
)

app.include_router(drivers.router)
app.include_router(disabled.router)
app.include_router(cars.router)
app.include_router(drive_requests.router)
app.include_router(shop_requests.router)
app.include_router(reviews.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok"}
