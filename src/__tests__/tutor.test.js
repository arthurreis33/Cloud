import { jest } from "@jest/globals";

// Mock do provider
jest.unstable_mockModule("../integrations/openRouterProvider.js", () => ({
    default: {
        generate: jest.fn().mockResolvedValue("Resposta mockada do tutor"),
    },
}));

process.env.OPENROUTER_API_KEY = "test-key";

const aiService = (await import("../core/aiService.js")).default;

describe("AI Service", () => {
    it("deve retornar resposta da IA", async () => {
        const response = await aiService.askAI(
            "Você é um tutor",
            "O que é cloud?"
        );
        expect(response).toBe("Resposta mockada do tutor");
    });
});

