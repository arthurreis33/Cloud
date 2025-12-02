import openRouterProvider from '../integrations/openRouterProvider.js';

// Serviço de IA
export async function askAI(systemPrompt, userPrompt) {
    return openRouterProvider.generate(systemPrompt, userPrompt);
}

export default { askAI };
