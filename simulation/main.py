from json import dumps, loads
from os import getenv
from threading import Lock, Thread
from time import sleep, time
from pika import BlockingConnection, URLParameters

from DistrictSimulation import DistrictSimulation


class SimulationService:
    def __init__(self):
        amqp_url = getenv('RABBITMQ_CONNECTION_STRING')

        print(f"🔌 Łączenie z RabbitMQ: {amqp_url}")

        self.rabbit_params = URLParameters(amqp_url)

        print("🏗️ Inicjalizowanie modelu fizycznego...")
        self.simulation = DistrictSimulation("district_config.yaml", "weather_history.csv")

        self.lock = Lock()
        self.is_started = False
        self.simulation_speed = 1.0
        self.simulation_step = 300

    def start(self):
        listener_thread = Thread(target=self._listen_for_commands, daemon=True)
        listener_thread.start()

        self._run_physics_loop()

    def _listen_for_commands(self):
        print("🎧 Podłączanie do RabbitMQ (Consumer)...")
        try:
            connection = BlockingConnection(self.rabbit_params)
            channel = connection.channel()

            channel.queue_declare(queue='district.commands', durable=True)

            def callback(ch, method, properties, body):
                try:
                    cmd = loads(body)
                    self._process_command(cmd)
                except Exception as e:
                    print(f"❌ Błąd przetwarzania komendy: {e}")

            channel.basic_consume(queue='district.commands', on_message_callback=callback, auto_ack=True)
            print("🎧 Nasłuchiwanie komend aktywne...")
            channel.start_consuming()
        except Exception as e:
            print(f"❌ Błąd połączenia RabbitMQ (Listener): {e}")
            sleep(5)
            self._listen_for_commands()

    def _process_command(self, cmd):
        with self.lock:
            msg_type = cmd.get("type")
            payload = cmd.get("payload", {})

            if msg_type == "SYSTEM":
                action = payload.get("action")

                if action == "START":
                    self.is_started = True
                    print("▶️ Otrzymano START")

                elif action == "STOP":
                    self.is_started = False
                    print("⏸️ Otrzymano STOP")

                elif action == "UPDATE_CONFIG":
                    if "simulation_speed" in payload:
                        self.simulation_speed = float(payload["simulation_speed"])
                        print(f"⏩ Prędkość zmieniona na: x{self.simulation_speed}")
                    if "simulation_step" in payload:
                        self.simulation_step = int(payload["simulation_step"])
                        print(f"⏱️ Krok symulacji zmieniony na: {self.simulation_step}s")

    def _run_physics_loop(self):
        pub_connection = BlockingConnection(self.rabbit_params)
        pub_channel = pub_connection.channel()
        pub_channel.queue_declare(queue='district.telemetry', durable=True)

        print("🚀 Gotowy do pracy. Czekam na sygnał START...")

        while True:
            with self.lock:
                started = self.is_started
                speed = self.simulation_speed
                step = self.simulation_step

            if not started:
                sleep(0.5)
                continue

            start_time = time()

            try:
                simulation_result = self.simulation.run_step(step)

                pub_channel.basic_publish(
                    exchange='',
                    routing_key='district.telemetry',
                    body=dumps(simulation_result)
                )

                target_sleep = step / speed

                compute_time = time() - start_time
                real_sleep = max(0.0, target_sleep - compute_time)

                print(f"Step: {step}s | Speed: x{speed} | Compute: {compute_time:.3f}s | Sleep: {real_sleep:.3f}s")
                sleep(real_sleep)

            except Exception as e:
                print(f"⚠️ Błąd w pętli fizycznej: {e}")
                sleep(1)


if __name__ == "__main__":
    service = SimulationService()
    service.start()
