// Configuração do OpenRouter
const API_URL = "https://openrouter.ai/api/v1/chat/completions";
const MODEL = "x-ai/grok-4.1-fast:free";

console.log('[AI] Inicializando provider - Key configurada:', !!process.env.OPENROUTER_API_KEY);

// Gera resposta da IA
async function generate(systemPrompt, userPrompt) {
    const maxRetries = 2;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        console.log(`[AI] Enviando requisição (${attempt}/${maxRetries})`);

        try {
            const response = await fetch(API_URL, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${process.env.OPENROUTER_API_KEY}`,
                    "Content-Type": "application/json",
                    "HTTP-Referer": process.env.APP_URL || "http://localhost:3000",
                    "X-Title": "IsCoolGPT"
                },
                body: JSON.stringify({
                    model: MODEL,
                    messages: [
                        { role: "system", content: systemPrompt },
                        { role: "user", content: userPrompt }
                    ]
                })
            });

            if (!response.ok) {
                const errorBody = await response.json().catch(() => ({}));
                throw new Error(errorBody.error?.message || `Erro HTTP ${response.status}`);
            }

            const data = await response.json();
            console.log('[AI] Resposta recebida da API');
            
            return data.choices?.[0]?.message?.content || "";

        } catch (error) {
            console.log(`[AI] Tentativa ${attempt} falhou:`, error.message);
            
            if (attempt < maxRetries) {
                console.log('[AI] Aguardando para nova tentativa...');
                await new Promise(resolve => setTimeout(resolve, 1500));
                continue;
            }
            
            throw new Error("Não foi possível obter resposta da IA");
        }
    }
}

export default { generate };
