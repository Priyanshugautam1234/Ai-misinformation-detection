# AI Misinformation Detection Platform

A multimodal AI-powered misinformation detection platform built using React, FastAPI, PyTorch, and scikit-learn.

## Features

- AI Scam Text Detection
- URL Reputation Analysis
- CNN-based Image Forensics
- Error Level Analysis (ELA)
- Metadata Integrity Analysis
- Real-time Threat Scoring
- AI Confidence Dashboard
- Report & Analytics System

## Tech Stack

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS

### Backend
- FastAPI
- PyTorch
- scikit-learn
- Pillow

## AI Models
- Logistic Regression (Text Scam Detection)
- ResNet18 CNN (AI Image Detection)

## Installation

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
