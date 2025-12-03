import os
from dotenv import load_dotenv
import uvicorn
from src.app import app

load_dotenv()

PORT = int(os.getenv('PORT', 3000))

if __name__ == '__main__':
    print(f'Servidor rodando em http://localhost:{PORT}')
    print('Pressione CTRL+C para parar.')
    uvicorn.run(app, host='0.0.0.0', port=PORT)

