import { askAI } from '../core/aiService.js';

// Handler de perguntas
export const handleQuestion = async (req, res) => {
    const { question } = req.body;

    console.log('[Tutor] Nova requisição recebida');

    if (!question || question.trim() === '') {
        console.log('[Tutor] Requisição sem pergunta');
        return res.status(400).json({ 
            error: 'Envie uma pergunta no campo "question"'
        });
    }

    console.log('[Tutor] Processando pergunta:', question.substring(0, 50) + '...');

    const systemPrompt = `Você é um tutor de Cloud Computing. Responda de forma clara e didática para estudantes universitários.`;

    try {
        const answer = await askAI(systemPrompt, question);
        console.log('[Tutor] Resposta gerada com sucesso');

        return res.status(200).json({
            question: question,
            answer: answer
        });

    } catch (err) {
        console.log('[Tutor] Falha ao gerar resposta:', err.message);
        return res.status(500).json({ 
            error: 'Erro ao processar pergunta'
        });
    }
};
