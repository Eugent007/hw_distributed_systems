import abc

import httpx


class ResultsObserver(abc.ABC):
    @abc.abstractmethod
    def observe(self, data: bytes) -> None: ...


async def do_reliable_request(url: str, observer: ResultsObserver) -> None:
    """
    Одна из главных проблем распределённых систем - это ненадёжность связи.

    Ваша задача заключается в том, чтобы таким образом исправить этот код, чтобы он
    умел переживать возвраты ошибок и таймауты со стороны сервера, гарантируя
    успешный запрос (в реальной жизни такая гарантия невозможна, но мы чуть упростим себе задачу).

    Все успешно полученные результаты должны регистрироваться с помощью обсёрвера.
    """

    async with httpx.AsyncClient() as client:
        while True:
            try:
                # Отключаем таймауты или ставим очень большие, чтобы пережить "медленный" сервер
                response = await client.get(
                    url,
                    timeout=httpx.Timeout(60.0, connect=10.0)  # большие таймауты
                )
                response.raise_for_status()
                data = response.read()
                observer.observe(data)
                return
            except (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError):
                # При любой ошибке связи или 5xx просто повторяем запрос
                # (в тестах сервер иногда "падает" или отвечает медленно)
                continue
