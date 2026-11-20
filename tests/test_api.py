import unittest
from datetime import date, timedelta
from unittest.mock import patch

import api


class AppointmentApiTests(unittest.TestCase):
    def setUp(self):
        self.consultas = []
        self.carregar_patch = patch(
            "api.carregar_consultas", side_effect=lambda: self.consultas
        )
        self.salvar_patch = patch(
            "api.salvar_consultas", side_effect=self._salvar_consultas
        )
        self.email_patch = patch("api.enviar_email_confirmacao")
        self.carregar_patch.start()
        self.salvar_patch.start()
        self.email_patch.start()
        self.addCleanup(self.carregar_patch.stop)
        self.addCleanup(self.salvar_patch.stop)
        self.addCleanup(self.email_patch.stop)
        api.app.config.update(TESTING=True)
        self.client = api.app.test_client()

    def _salvar_consultas(self, consultas):
        self.consultas[:] = consultas

    def _payload(self):
        return {
            "paciente": "Ana Souza",
            "telefone": "(11) 99999-1234",
            "email": "ana@example.com",
            "especialidade": "Cardiologia",
            "medico": "Dr. João",
            "data": (date.today() + timedelta(days=1)).isoformat(),
            "horario": "10:00",
        }

    def test_booking_reserves_slot_and_removes_it_from_availability(self):
        response = self.client.post("/api/appointments", json=self._payload())

        self.assertEqual(response.status_code, 201)
        appointment = response.get_json()["consulta"]
        self.assertEqual(appointment["data"], (date.today() + timedelta(days=1)).strftime("%d/%m/%Y"))
        self.assertEqual(len(self.consultas), 1)

        availability = self.client.get(
            "/api/availability",
            query_string={
                "especialidade": appointment["especialidade"],
                "medico": appointment["medico"],
                "data": self._payload()["data"],
            },
        )
        self.assertEqual(availability.status_code, 200)
        self.assertNotIn("10:00", availability.get_json()["horarios"])

    def test_double_booking_is_rejected(self):
        payload = self._payload()
        self.client.post("/api/appointments", json=payload)

        response = self.client.post("/api/appointments", json=payload)

        self.assertEqual(response.status_code, 409)
        self.assertEqual(len(self.consultas), 1)

    def test_invalid_doctor_and_date_are_rejected(self):
        payload = self._payload()
        payload["medico"] = "Dr. inexistente"
        invalid_doctor = self.client.post("/api/appointments", json=payload)
        self.assertEqual(invalid_doctor.status_code, 400)

        payload = self._payload()
        payload["data"] = "2020-01-01"
        invalid_date = self.client.post("/api/appointments", json=payload)
        self.assertEqual(invalid_date.status_code, 400)
        self.assertEqual(self.consultas, [])

    def test_appointment_can_be_cancelled(self):
        self.client.post("/api/appointments", json=self._payload())
        appointment_id = self.consultas[0]["id"]

        response = self.client.delete(f"/api/appointments/{appointment_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.consultas, [])


if __name__ == "__main__":
    unittest.main()
