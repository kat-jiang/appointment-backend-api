from urllib import response
from fastapi import FastAPI, status, Response
from schema import Doctor, Appointment, UpdateAppointment
from datetime import datetime, date

app = FastAPI()

DOCTORS = {
	"0": {
		"doctor_id": "0",
		"first_name": "Test",
		"last_name": "Doc-0",
	},
	"1": {
		"doctor_id": "1",
		"first_name": "Test",
		"last_name": "Doc-1",
	},
	"2": {
		"doctor_id": "2",
		"first_name": "Test",
		"last_name": "Doc-2",
	}
}

APPOINTMENTS = {
	1 : Appointment(
        doctor_id="0",
        first_name="Patient",
        last_name="A",
        datetime=datetime(2022, 7, 22, 10, 15),
        kind="New Patient"
    ),
	2: Appointment(
        doctor_id="0",
        first_name="Patient",
        last_name="B",
        datetime=datetime(2022, 7, 22, 10, 15),
        kind="Follow-up"
    ),
    3: Appointment(
        doctor_id="0",
        first_name="Patient",
        last_name="C",
        datetime=datetime(2022, 7, 22, 10, 15),
        kind="Follow-up"
    ),
	4: Appointment(
        doctor_id="1",
        first_name="Patient",
        last_name="D",
        datetime=datetime(2022, 7, 22, 14),
        kind="New Patient"
    )
}

#used to autoincrement the appointment id
#currently set to 4 because of last appointment id in APPOINTMENTS
COUNT = 4


@app.get("/doctors")
def fetch_doctors():

    return DOCTORS


@app.get("/doctor/{doctor_id}/appointments/", status_code=200)
def get_doctor_schedule(doctor_id:str, appointment_date:str, response:Response):
    schedule = {}
    try:
        appointment_date = date.fromisoformat(appointment_date)
    except:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'detail': "Input date must be in isoformat YYYY-MM-DD"}

    if DOCTORS.get(doctor_id) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'detail': f"Doctor with id {doctor_id} does not exist"}

    for appointment_id, data in APPOINTMENTS.items():
        if data.doctor_id == doctor_id and data.datetime.date() == appointment_date:
            schedule[appointment_id] = APPOINTMENTS[appointment_id]

    if not schedule:
        return {'detail': 'No appointments are scheduled for this date'}

    return schedule


@app.post("/doctor/appointment", status_code=status.HTTP_201_CREATED)
def create_appointment(request:Appointment, response:Response):
    if request.datetime.minute % 15 != 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'detail': "Appointment times must be in 15 minutes intervals (00, 15, 30, 45)"}

    doctor = DOCTORS.get(request.doctor_id)
    if not doctor:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'detail': f"Doctor with id {request.doctor_id} does not exist"}

    request.datetime = request.datetime.replace(second=0, microsecond=0, tzinfo=None)

    schedule = []
    for appointment_id, data in APPOINTMENTS.items():
        if data.doctor_id == request.doctor_id and data.datetime == request.datetime:
            schedule.append(APPOINTMENTS[appointment_id])
        if len(schedule) >= 3:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {'detail': "Appointment slots for that time is full, please try another time"}

    global COUNT
    COUNT += 1

    APPOINTMENTS[COUNT] = request

    return {'detail': f"Appointment created with id {COUNT}"}


@app.delete("/appointment/{appointment_id}", status_code=200)
def delete_appointment(appointment_id: int, response:Response):

    appointment = APPOINTMENTS.get(appointment_id)
    if appointment:
        del APPOINTMENTS[appointment_id]
        return {'details': f'Appointment id {appointment_id} deleted'}

    response.status_code = status.HTTP_404_NOT_FOUND
    return {'details': f'Appointment id {appointment_id} does not exist'}


@app.patch("/appointment/{appointment_id}", status_code=200)
def update_appointment(appointment_id: int, request: UpdateAppointment, response:Response):
    if request.doctor_id:
        doctor = DOCTORS.get(request.doctor_id)
        if not doctor:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {'detail': f"Doctor with id {request.doctor_id} does not exist"}

    appointment = APPOINTMENTS.get(appointment_id)
    if appointment is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'details': f'Appointment id {appointment_id} does not exist'}

    if request.datetime:
        if request.datetime.minute % 15 != 0:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {'detail': "Appointment times must be in 15 minutes intervals (00, 15, 30, 45)"}

        request.datetime = request.datetime.replace(second=0, microsecond=0, tzinfo=None)

        schedule = []
        for appointment_id, data in APPOINTMENTS.items():
            if data.doctor_id == request.doctor_id and data.datetime == request.datetime:
                schedule.append(APPOINTMENTS[appointment_id])
            if len(schedule) >= 3:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {'detail': "Appointment slots for that time is full, please try another time"}

    old_appointment = APPOINTMENTS[appointment_id]
    new_appointment = request.dict(exclude_unset=True)
    updated_appointment = old_appointment.copy(update=new_appointment)
    APPOINTMENTS[appointment_id] = updated_appointment

    return {'detail': 'Appointment updated'}
