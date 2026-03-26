from fastapi import FastAPI
import drivers, disabled, cars, drive_requests, shop_requests, reviews, other_requests
import auth_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Mobility CRUD API",
    description="CRUD API for drivers, disabled users, cars, requests and reviews",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # your SvelteKit dev URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(drivers.router)
app.include_router(disabled.router)
app.include_router(cars.router)
app.include_router(drive_requests.router)
app.include_router(shop_requests.router)
app.include_router(reviews.router)
app.include_router(other_requests.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok"}
