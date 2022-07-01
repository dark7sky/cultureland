FROM dragom/pychrome
WORKDIR /app
COPY requirements.txt /app/.
RUN pip install --no-cache-dir -r requirements.txt
COPY cookies.py /app/.
COPY cult.py /app/.
ENV TZ 'Asia/Seoul'
ENV ID ''
ENV PSSWD ''
ENV my_token ''
ENV users_id ''
CMD ["python","cult.py"]