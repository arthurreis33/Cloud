import request from "supertest";
import express from "express";
import router from "../routes/index.js";

const app = express();
app.use(express.json());
app.use(router);

describe("API Routes", () => {
    describe("GET /", () => {
        it("retorna status da API", async () => {
            const response = await request(app).get("/");
            
            expect(response.status).toBe(200);
            expect(response.body.status).toBe("online");
            expect(response.body.service).toBe("IsCoolGPT");
        });
    });

    describe("POST /api/tutor/ask", () => {
        it("retorna erro sem pergunta", async () => {
            const response = await request(app)
                .post("/api/tutor/ask")
                .send({});
            
            expect(response.status).toBe(400);
        });
    });
});
