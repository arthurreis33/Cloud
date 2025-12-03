import os
import asyncio
import httpx

# Configuração do modelo OpenRouter
LLM_MODEL = 'openai/gpt-oss-20b:free'
API_ENDPOINT = 'https://openrouter.ai/api/v1/chat/completions'

print(f'[LLM] Inicializando cliente OpenRouter - Chave configurada: {bool(os.getenv("OPENROUTER_API_KEY"))}')

# Cria resposta da IA usando streaming
async def create_response(instruction: str, user_query: str) -> str:
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not api_key:
        raise Exception('OPENROUTER_API_KEY não configurada. Configure no arquivo .env')
    
    max_attempts = 3
    
    for attempt in range(1, max_attempts + 1):
        print(f'[LLM] Enviando solicitação ({attempt}/{max_attempts})')

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Requisição com streaming
                async with client.stream(
                    'POST',
                    API_ENDPOINT,
                    headers={
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json',
                        'HTTP-Referer': os.getenv('APP_URL', 'http://localhost:3000'),
                        'X-Title': 'IsCoolGPT'
                    },
                    json={
                        'model': LLM_MODEL,
                        'messages': [
                            {
                                'role': 'system',
                                'content': instruction
                            },
                            {
                                'role': 'user',
                                'content': user_query
                            }
                        ],
                        'stream': True
                    }
                ) as response:
                    
                    if not response.is_success:
                        # Lê o corpo da resposta de erro
                        error_text = b""
                        async for chunk in response.aiter_bytes():
                            error_text += chunk
                        
                        try:
                            import json
                            error_body = json.loads(error_text.decode('utf-8'))
                            error_message = error_body.get('error', {}).get('message', f'Erro HTTP {response.status_code}')
                        except:
                            error_message = f'Erro HTTP {response.status_code}: {error_text.decode("utf-8", errors="ignore")}'
                        raise Exception(error_message)
                    
                    # Processa stream linha por linha (formato SSE)
                    full_response = ""
                    import json
                    
                    async for line_bytes in response.aiter_lines():
                        line = line_bytes.decode('utf-8') if isinstance(line_bytes, bytes) else line_bytes
                        
                        if not line or line.strip() == '':
                            continue
                        
                        # Formato SSE: "data: {...}" ou apenas "{...}"
                        if line.startswith('data: '):
                            line = line[6:].strip()
                        
                        if line == '[DONE]' or line.strip() == '':
                            continue
                        
                        try:
                            chunk_data = json.loads(line)
                            
                            # Extrai conteúdo do chunk
                            if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                choice = chunk_data['choices'][0]
                                delta = choice.get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    full_response += content
                            
                            # Verifica informações de uso (vem no último chunk)
                            if 'usage' in chunk_data:
                                usage = chunk_data['usage']
                                if 'reasoning_tokens' in usage:
                                    print(f'[LLM] Tokens de raciocínio: {usage["reasoning_tokens"]}')
                        
                        except json.JSONDecodeError:
                            # Ignora linhas que não são JSON válido
                            continue
                        except Exception as e:
                            print(f'[LLM] Erro ao processar chunk: {str(e)}')
                            continue
                    
                    print('[LLM] Resposta completa recebida')
                    
                    if not full_response:
                        raise Exception('Resposta vazia da API')
                    
                    return full_response

        except Exception as error:
            print(f'[LLM] Tentativa {attempt} falhou: {str(error)}')
            
            if attempt < max_attempts:
                print('[LLM] Aguardando antes de tentar novamente...')
                await asyncio.sleep(2.0)
                continue
            
            raise Exception('Não foi possível obter resposta do modelo de linguagem')
