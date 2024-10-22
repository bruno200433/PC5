import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

wine_data_url = 'https://github.com/gdelgador/ProgramacionPython202401/raw/main/Modulo5/src/winemag-data-130k-v2.csv'
country_continent_url = 'https://gist.githubusercontent.com/kintero/7d1db891401f56256c79/raw/a61f6d0dda82c3f04d2e6e76c3870552ef6cf0c6/paises.csv'

df_wine = pd.read_csv(wine_data_url)

print("Primeras filas del DataFrame:")
print(df_wine.head())
print("\nResumen del DataFrame:")
print(df_wine.info())

df_wine.rename(columns={
    'country': 'país',
    'region_1': 'región',
    'points': 'puntos',
    'price': 'precio'
}, inplace=True)

# Crear nuevas columnas
continent_data = pd.read_csv(country_continent_url)
continent_mapping = continent_data.set_index('Country')['Continent'].to_dict()

df_wine['continente'] = df_wine['país'].map(continent_mapping)

df_wine['precio_categoria'] = df_wine['precio'].apply(lambda x: 'Alto' if x > 100 else 'Bajo')

df_wine['reseñas'] = df_wine['puntos'].apply(lambda x: 1 if x >= 90 else 0)

# Generar reportes
report1 = df_wine.groupby('continente')[['puntos', 'precio']].max().reset_index()

report2 = df_wine.groupby('país')[['precio', 'reseñas']].agg({'precio': 'mean', 'reseñas': 'sum'}).reset_index()
report2.sort_values(by='precio', ascending=False, inplace=True)

report3 = df_wine['precio_categoria'].value_counts().reset_index()
report3.columns = ['categoría', 'cantidad']

report4 = df_wine[df_wine['puntos'] > 95][['país', 'región', 'puntos', 'precio']]

# Exportar reportes a diferentes formatos
report1.to_csv('reporte_vinos_por_continente.csv', index=False)
report2.to_excel('reporte_precio_reseñas_por_pais.xlsx', index=False)
report3.to_sql('vinos_categoria_precio', 'sqlite:///vinos.db', index=False, if_exists='replace')
report4.to_json('vinos_puntuaciones_altas.json', orient='records')

smtp_server = 'smtp.gmail.com'
smtp_port = 587
sender_email = 'bruedu07@gmail.com'
sender_password = open('token.txt').read().strip()

receiver_email = 'bruedu07@gmail.com'
subject = 'Reporte de Vinos'
body = 'Adjunto el reporte de vinos mejor puntuados por continente.'

msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))

file_path = 'reporte_vinos_por_continente.csv'
with open(file_path, 'rb') as file:
    attachment = MIMEApplication(file.read(), _subtype="csv")
    attachment.add_header('Content-Disposition', 'attachment', filename='reporte_vinos_por_continente.csv')
    msg.attach(attachment)

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()  # Iniciar el modo seguro
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())

print('Correo enviado exitosamente')