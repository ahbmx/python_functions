Perfecto — aquí tienes una versión más simple y eficiente:

✔ No ordena resultados
✔ Solo espera a que todas las tareas terminen
✔ Sigue teniendo logging + barra de progreso
✔ Devuelve los resultados en el orden en que van terminando


---

✅ ParallelExecutor (sin resultados ordenados)

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
        No mantiene el orden original de envío.
        Retorna los resultados conforme vayan completándose.
        """
        total = len(self.futures)
        self.logger.info(f"Esperando finalización de {total} tareas...")

        progress_bar = tqdm(total=total, disable=not self.progress_enabled)

        results = []

        for future in as_completed(self.futures):
            try:
                res = future.result()
                results.append(res)
                self.logger.info(f"Tarea completada: {res}")
            except Exception as e:
                results.append(e)
                self.logger.error(f"Error en tarea: {e}")

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

def tarea(n, delay):
    time.sleep(delay)
    return f"Tarea {n} terminada tras {delay}s"

px = ParallelExecutor(max_workers=4, mode="thread", progress=True)

px.submit(tarea, 1, 3)
px.submit(tarea, 2, 1)
px.submit(tarea, 3, 2)
px.submit(tarea, 4, 4)

resultados = px.run_wait_all()
print("Resultados:", resultados)

px.shutdown()


---

✔ Diferencias clave respecto a la versión anterior

Comportamiento	Antes	Ahora

Orden de resultados	Ordenados por envío	Ordenados por finalización
Complejidad	Mayor	✔ Más simple
Uso	Automatización rápida	✔ Ideal para tareas independientes



---

Si quieres, puedo agregar:

contador de errores

nombres personalizados por tarea

integración con subprocess para ejecutar comandos de storage

límites de reintentos

timeout por tarea


¿Quieres alguna de esas mejoras?
