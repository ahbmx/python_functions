Perfecto — aquí tienes la clase ParallelExecutor con barra de progreso integrada usando tqdm, manteniendo logging y esperando a que todas las tareas terminen.

La barra de progreso avanza conforme cada tarea termina.


---

✅ ParallelExecutor con tqdm + logging

import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from tqdm import tqdm


class ParallelExecutor:
    def __init__(self, max_workers=10, mode="thread", logger=None, progress=True):
        """
        mode = 'thread'  → ThreadPoolExecutor
        mode = 'process' → ProcessPoolExecutor
        """
        self.logger = logger or self._create_default_logger()
        self.progress_enabled = progress

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
        self.logger.info(f"Enviando tarea: {fn.__name__} args={args} kwargs={kwargs}")
        future = self.executor.submit(fn, *args, **kwargs)
        self.futures.append(future)
        return future

    def run_wait_all(self):
        """
        Espera a que TODAS las tareas terminen.
        Muestra barra de progreso indicando tareas completadas.
        Retorna los resultados en orden de envío.
        """
        total = len(self.futures)
        self.logger.info(f"Esperando a que todas las tareas terminen... total={total}")

        results = [None] * total

        # Barra de progreso
        progress_bar = tqdm(total=total, disable=not self.progress_enabled)

        future_to_index = {future: idx for idx, future in enumerate(self.futures)}

        for future in as_completed(self.futures):
            idx = future_to_index[future]
            try:
                res = future.result()
                results[idx] = res
                self.logger.info(f"Tarea #{idx} completada con resultado: {res}")
            except Exception as e:
                results[idx] = e
                self.logger.error(f"Error en tarea #{idx}: {e}")

            progress_bar.update(1)

        progress_bar.close()
        self.logger.info("Todas las tareas han terminado.")
        return results

    def shutdown(self):
        self.logger.info("Cerrando executor...")
        self.executor.shutdown(wait=True)
        self.logger.info("Executor cerrado.")


---

🧪 Ejemplo de uso

import time

def tarea(num, delay):
    time.sleep(delay)
    return f"Tarea {num} después de {delay}s"

px = ParallelExecutor(
    max_workers=4,
    mode="thread",
    progress=True
)

px.submit(tarea, 1, 2)
px.submit(tarea, 2, 3)
px.submit(tarea, 3, 1)
px.submit(tarea, 4, 5)

resultados = px.run_wait_all()
print("Resultados finales:", resultados)

px.shutdown()


---

✔ Características añadidas

Funcionalidad	Estado

Logging integrado	✔
Barra de progreso (tqdm)	✔
Espera a todas las tareas	✔
Resultados ordenados	✔
Manejo de excepciones	✔
Modo thread/process	✔
No usa asyncio	✔



---

¿Quieres que la barra de progreso muestre algo más?

Puedo hacer que muestre:

tiempo estimado restante

nombre de la tarea

número de tareas fallidas

barra por grupos de tareas

progreso por tipo de operación (ej: volúmenes, snapshots, etc.)


¿Quieres extenderla más?
