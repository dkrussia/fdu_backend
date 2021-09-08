from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str
    password: str
    fingerprint: str


class UserData(BaseModel):
    username: str
    email: str

    class Config:
        orm_mode = True


class RefreshTokenData(BaseModel):
    refresh_token: str
    fingerprint: str

class GoogleLogin(BaseModel):
    id_token: str
    fingerprint: str

