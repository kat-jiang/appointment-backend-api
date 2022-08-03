from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class Doctor(BaseModel):
    doctor_id: str
    fname: str
    lname: str

class Appointment(BaseModel):
    doctor_id: str
    first_name: str
    last_name: str
    datetime: datetime
    kind: str

class UpdateAppointment(BaseModel):
    doctor_id: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    datetime: Optional[datetime]
    kind: Optional[str]

