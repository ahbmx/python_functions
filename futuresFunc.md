Perfecto — aquí tienes una versión mejorada de la clase, que incluye:

✔ logging integrado
✔ Uso simple
✔ Espera a que todas las tareas terminen (solo modo “wait all”)
✔ Captura de excepciones con logging
✔ Resultados devueltos en el orden en que se enviaron


---

✅ Clase ParallelExecutor con logging integrado

import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

class ParallelExecutor:
    def __init__(self, max_workers=10, mode="thread", logger=None):
        """
        mode = 'thread'  → ThreadPoolExecutor
        mode = 'process' → ProcessPoolExecutor
        """
        self.logger = logger or self._create_default_logger()

        if mode == "thread":
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
        elif mode == "process":
            self.executor = ProcessPoolExecutor(max_workers=max_workers)
        else:
            raise ValueError("mode debe ser 'thread' o 'process'")

        self.futures = []
        self.logger.info(f"ParallelExecutor iniciado con {max_workers} workers en modo {mode}")

    def _create_default_logger(self):
        logger = logging.getLogger("ParallelExecutor")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "[%(asctime)s] %(levelname)s - %(message)s",
                "%H:%M:%S"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def submit(self, fn, *args, **kwargs):
        """
        Encola una función con múltiples parámetros.
        """
        self.logger.info(f"Enviando tarea: {fn.__name__} args={args} kwargs={kwargs}")
        future = self.executor.submit(fn, *args, **kwargs)
        self.futures.append(future)
        return future

    def run_wait_all(self):
        """
        Espera a que TODAS las tareas terminen.
        Retorna los resultados en orden de envío.
        """
        self.logger.info("Esperando a que todas las tareas terminen...")

        results = []
        for future in self.futures:
            try:
                res = future.result()
                self.logger.info(f"Tarea completada con resultado: {res}")
                results.append(res)
            except Exception as e:
                self.logger.error(f"Error en tarea: {e}")
                results.append(e)

        self.logger.info("Todas las tareas han terminado.")
        return results

    def shutdown(self):
        self.logger.info("Cerrando executor...")
        self.executor.shutdown(wait=True)
        self.logger.info("Executor cerrado.")


---

🧪 Ejemplo de uso

import time

def tarea(n, delay=1):
    time.sleep(delay)
    return f"Resultado {n}"

px = ParallelExecutor(max_workers=3, mode="thread")

px.submit(tarea, 1, delay=2)
px.submit(tarea, 2, delay=1)
px.submit(tarea, 3, delay=3)

resultados = px.run_wait_all()
print("Resultados finales:", resultados)

px.shutdown()


---

✔ ¿Qué incluye esta versión?

Funcionalidad	Estado

Logging integrado	✅
Espera a que todas las tareas terminen	✅
Resultado ordenado por envío	✅
Manejo de excepciones por tarea	✅
Configurable: threads/procesos	✅
API simple y limpia	✅



---

🔧 ¿Quieres agregar algo?

Puedo añadir fácilmente:

niveles de logging configurables

timeout por tarea

reintentos

métricas (tiempos por tarea)

identificación de tareas por nombre

una barra de progreso (tqdm)


¿Quieres extender la clase?
