import { Router } from 'express';
import { handleQuestion } from '../handlers/tutorHandler.js';

const router = Router();

// POST /api/tutor/ask - Faz uma pergunta ao tutor
router.post('/ask', handleQuestion);

export default router;

