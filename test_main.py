from fastapi.testclient import TestClient
from main import app, DOCTORS
from datetime import datetime

client = TestClient(app)


def test_get_doctors():
    response = client.get("/doctors")
    assert response.status_code == 200
    assert response.json() == DOCTORS


def test_get_doctor_appointments_success():
    doctor_id = "1"
    response = client.get(f"/doctor/{doctor_id}/appointments/",
        params={
            'doctor_id' : doctor_id,
            'appointment_date' : "2022-07-22"
    })
    assert response.status_code == 200
    assert response.json() == {
        "4": {
            'doctor_id': doctor_id,
            'first_name':"Patient",
            'last_name':"D",
            'datetime':'2022-07-22T14:00:00',
            'kind':"New Patient"
        }
    }


def test_get_doctor_appointments_no_schedule():
    doctor_id = "1"
    response = client.get(f"/doctor/{doctor_id}/appointments/",
        params={
            'doctor_id' : doctor_id,
            'appointment_date' : "2022-07-25"
    })
    assert response.status_code == 200
    assert response.json() == {'detail': 'No appointments are scheduled for this date'}


def test_get_doctor_appointments_invalid_doctor():
    doctor_id = "4"
    response = client.get(f"/doctor/{doctor_id}/appointments/",
        params={
            'doctor_id' : doctor_id,
            'appointment_date' : "2022-07-22"
    })
    assert response.status_code == 404
    assert response.json() == {'detail': f"Doctor with id {doctor_id} does not exist"}


def test_get_doctor_appointments_invalid_date():
    doctor_id = "1"
    response = client.get(f"/doctor/{doctor_id}/appointments/",
        params={
            'doctor_id' : doctor_id,
            'appointment_date' : "07-22-2022"
    })
    assert response.status_code == 400
    assert response.json() == {'detail': "Input date must be in isoformat YYYY-MM-DD"}


def test_create_appointment_success():
    data = {
            'doctor_id': "1",
            'first_name':"Patient",
            'last_name':"D",
            'datetime':'2022-07-22T14:00:00',
            'kind':"New Patient"
    }
    response = client.post("/doctor/appointment",
        json=data
    )
    assert response.status_code == 201
    assert response.json() == {'detail': f"Appointment created with id 5"}


def test_create_appointment_invalid_doctor():
    doctor_id = "5"
    response = client.post("/doctor/appointment",
        json={
            'doctor_id': doctor_id,
            'first_name':"Patient",
            'last_name':"D",
            'datetime':'2022-07-22T14:00:00',
            'kind':"New Patient"
        }
    )
    assert response.status_code == 404
    assert response.json() == {'detail': f"Doctor with id {doctor_id} does not exist"}


def test_create_appointment_invalid_time():
    doctor_id = "1"
    response = client.post("/doctor/appointment",
        json={
            'doctor_id': doctor_id,
            'first_name':"Patient",
            'last_name':"D",
            'datetime':'2022-07-22T14:20:00',
            'kind':"New Patient"
        }
    )
    assert response.status_code == 400
    assert response.json() == {'detail': "Appointment times must be in 15 minutes intervals (00, 15, 30, 45)"}


def test_create_appointment_overbooked():
    doctor_id = "0"
    response = client.post("/doctor/appointment",
        json={
            'doctor_id': doctor_id,
            'first_name':"Patient",
            'last_name':"D",
            'datetime':'2022-07-22T10:15:00',
            'kind':"New Patient"
        }
    )
    assert response.status_code == 400
    assert response.json() == {'detail': "Appointment slots for that time is full, please try another time"}


def test_update_appointment_success():
    appointment_id = 4
    response = client.patch(f"/appointment/{appointment_id}",
        params={
            'appointment_id': appointment_id
        },
        json={
            'doctor_id': "2",
            'first_name':"Patient",
            'last_name':"EFG",
            'datetime':'2022-08-22T10:15:00',
            'kind':"New Patient"
        }
    )
    assert response.status_code == 200
    assert response.json() == {'detail': 'Appointment updated'}


def test_update_appointment_invalid_doctor():
    appointment_id = 4
    doctor_id = "3"
    response = client.patch(f"/appointment/{appointment_id}",
        params={
            'appointment_id': appointment_id
        },
        json={
            'doctor_id': doctor_id
        }
    )
    assert response.status_code == 404
    assert response.json() == {'detail': f"Doctor with id {doctor_id} does not exist"}


def test_update_appointment_invalid_id():
    appointment_id = 6
    response = client.patch(f"/appointment/{appointment_id}",
        params={
            'appointment_id': appointment_id
        },
        json={
            'doctor_id': "2",
            'first_name':"Patient",
            'last_name':"EFG",
            'datetime':'2022-08-22T10:15:00',
            'kind':"New Patient"
        }
    )
    assert response.status_code == 404
    assert response.json() == {'details': f'Appointment id {appointment_id} does not exist'}


def test_update_appointment_invalid_datetime():
    appointment_id = 4
    response = client.patch(f"/appointment/{appointment_id}",
        params={
            'appointment_id': appointment_id
        },
        json={
            'doctor_id': "2",
            'first_name':"Patient",
            'last_name':"EFG",
            'datetime':'2022-08-22T10:25:00',
            'kind':"New Patient"
        }
    )
    assert response.status_code == 400
    assert response.json() == {'detail': "Appointment times must be in 15 minutes intervals (00, 15, 30, 45)"}


def test_update_appointment_overbooked():
    appointment_id = 4
    response = client.patch(f"/appointment/{appointment_id}",
        params={
            'appointment_id': appointment_id
        },
        json={
            'doctor_id': "0",
            'datetime':'2022-07-22T10:15:00',
        }
    )
    assert response.status_code == 400
    assert response.json() == {'detail': "Appointment slots for that time is full, please try another time"}


def test_delete_appointment_success():
    appointment_id = 1
    response = client.delete(f"/appointment/{appointment_id}",
        params={'appointment_id': appointment_id}
    )
    assert response.status_code == 200
    assert response.json() == {'details': f'Appointment id {appointment_id} deleted'}


def test_delete_appointment_invalid_id():
    appointment_id = 6
    response = client.delete(f"/appointment/{appointment_id}",
        params={'appointment_id': appointment_id}
    )
    assert response.status_code == 404
    assert response.json() == {'details': f'Appointment id {appointment_id} does not exist'}