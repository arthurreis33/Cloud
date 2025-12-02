import { Router } from 'express';
import tutorRoutes from './tutorRoutes.js';

const router = Router();

// Health check / Info
router.get('/', (req, res) => {
    res.status(200).json({
        status: 'online',
        service: 'IsCoolGPT',
        version: '1.0.0',
        endpoints: {
            tutor: '/api/tutor/ask'
        }
    });
});

// Rotas do tutor
router.use('/api/tutor', tutorRoutes);

export default router;
