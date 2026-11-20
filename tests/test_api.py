import unittest
from datetime import date, timedelta
from unittest.mock import patch

import api


class AppointmentApiTests(unittest.TestCase):
    def setUp(self):
        self.consultas = []
        self.usuarios = []
        self.carregar_consultas_patch = patch(
            "api.carregar_consultas", side_effect=lambda: self.consultas
        )
        self.salvar_consultas_patch = patch(
            "api.salvar_consultas", side_effect=self._salvar_consultas
        )
        self.carregar_usuarios_patch = patch(
            "api.carregar_usuarios", side_effect=lambda: self.usuarios
        )
        self.salvar_usuarios_patch = patch(
            "api.salvar_usuarios", side_effect=self._salvar_usuarios
        )
        self.email_patch = patch("api.enviar_email_confirmacao")
        for patcher in (
            self.carregar_consultas_patch,
            self.salvar_consultas_patch,
            self.carregar_usuarios_patch,
            self.salvar_usuarios_patch,
            self.email_patch,
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

        api.app.config.update(TESTING=True, SECRET_KEY="test-secret")
        self.client = api.app.test_client()
        response = self.client.post("/api/auth/register", json=self._account())
        self.assertEqual(response.status_code, 201)
        self.user = response.get_json()["usuario"]

    def _salvar_consultas(self, consultas):
        self.consultas[:] = consultas

    def _salvar_usuarios(self, usuarios):
        self.usuarios[:] = usuarios

    def _account(self, email="ana@example.com", name="Ana Souza"):
        return {
            "nome": name,
            "telefone": "(11) 99999-1234",
            "email": email,
            "senha": "senha-segura-123",
        }

    def _payload(self):
        return {
            "paciente": "Nome falsificado",
            "telefone": "000000000",
            "email": "outra@example.com",
            "especialidade": "Cardiologia",
            "medico": "Dr. João",
            "data": (date.today() + timedelta(days=1)).isoformat(),
            "horario": "10:00",
        }

    def _register_other_user(self, client):
        response = client.post(
            "/api/auth/register",
            json=self._account(email="bruno@example.com", name="Bruno Lima"),
        )
        self.assertEqual(response.status_code, 201)
        return response.get_json()["usuario"]

    def test_booking_uses_authenticated_profile_and_updates_availability(self):
        response = self.client.post("/api/appointments", json=self._payload())

        self.assertEqual(response.status_code, 201)
        appointment = response.get_json()["consulta"]
        self.assertEqual(appointment["paciente"], "Ana Souza")
        self.assertEqual(appointment["email"], "ana@example.com")
        self.assertEqual(appointment["data"], (date.today() + timedelta(days=1)).strftime("%d/%m/%Y"))
        self.assertNotIn("usuario_id", appointment)
        self.assertEqual(self.consultas[0]["usuario_id"], self.user["id"])

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

    def test_appointments_are_private_to_the_authenticated_account(self):
        self.client.post("/api/appointments", json=self._payload())
        other_client = api.app.test_client()
        other_user = self._register_other_user(other_client)

        own_appointments = self.client.get("/api/appointments")
        other_appointments = other_client.get("/api/appointments")

        self.assertEqual(len(own_appointments.get_json()), 1)
        self.assertNotIn("usuario_id", own_appointments.get_json()[0])
        self.assertEqual(other_appointments.get_json(), [])
        self.assertNotEqual(self.user["id"], other_user["id"])

    def test_unauthenticated_users_cannot_read_or_create_appointments(self):
        anonymous = api.app.test_client()

        self.assertEqual(anonymous.get("/api/appointments").status_code, 401)
        self.assertEqual(
            anonymous.post("/api/appointments", json=self._payload()).status_code,
            401,
        )

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

    def test_user_cannot_cancel_another_users_appointment(self):
        self.client.post("/api/appointments", json=self._payload())
        appointment_id = self.consultas[0]["id"]
        other_client = api.app.test_client()
        self._register_other_user(other_client)

        forbidden_cancel = other_client.delete(
            f"/api/appointments/{appointment_id}"
        )
        own_cancel = self.client.delete(f"/api/appointments/{appointment_id}")

        self.assertEqual(forbidden_cancel.status_code, 404)
        self.assertEqual(own_cancel.status_code, 200)
        self.assertEqual(self.consultas, [])

    def test_login_does_not_return_password_hash(self):
        client = api.app.test_client()
        response = client.post(
            "/api/auth/login",
            json={"email": "ANA@example.com", "senha": "senha-segura-123"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("senha_hash", response.get_json()["usuario"])
        self.assertEqual(client.get("/api/auth/me").status_code, 200)


if __name__ == "__main__":
    unittest.main()
