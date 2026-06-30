■ PROJET TECHCORP — Challenge IA 7h
■ Briefing de Mission
Contexte : Vous êtes la nouvelle équipe technique de TechCorp Industries. L'équipe précédente a été licenciée
suite à des soupçons de compromission du code et des données. Vous devez reprendre leur travail, valider
l'intégrité du projet et finaliser le déploiement.
■ Objectifs Principaux
■ Mission Critique — Production Ready
Déployer le modèle Phi-3.5-Financial avec une interface chat :
• Serveur d'inférence opérationnel avec Phi-3.5-Financial — au choix de votre équipe :
• Ollama (solution clé en main recommandée)
• Triton Inference Server (solution avancée, configuration fournie)
• Serveur maison (FastAPI, Flask, vLLM… tout ce qui expose une API)
• Interface web obligatoire pour interagir avec le modèle en temps réel
• Documentation technique de votre déploiement
■ Mission Expérimentale — R&D;
Fine-tuner un modèle médical expérimental (pas pour production) :
• Fine-tuning LoRA d'un modèle de base avec dataset médical fourni
• Tests et validation des performances conversationnelles
• Note : Ce modèle reste expérimental, pas besoin de le déployer en production
■ Ressources à Disposition
■■ Infrastructure Technique
• Ollama — Serveur d'inférence local, solution la plus simple (ollama.com/download)
• Triton Inference Server — Déploiement avancé, configuration fournie dans tritton_server/
• Serveur maison — FastAPI, vLLM, llama.cpp… tout ce qui expose une API REST
• Phi-3.5-Financial — Modèle spécialisé finance/business, prêt à l'emploi (voir models/phi3_financial/)
• Dataset médical — Pour fine-tuning expérimental
• Google Colab Pro — GPU pour fine-tuning et tests
■ Fichiers Hérités de l'Équipe Précédente
• Code d'entraînement et de fine-tuning LoRA pour le modèle financier
• Modèle Phi-3.5-Financial pré-entraîné
• Code pour un chatbot de base
• Quelques configurations de serveurs d'inférence (Ollama, Triton, etc.)
• Dataset de conversations médicales (format JSON)
• Documentation technique partielle
• Quelques fichiers de logs et notes personnelles laissés sur les machines
■ Pistes Techniques
• Quantization : Envisagez des modèles quantisés (4-bit/8-bit) pour optimiser les performances
• Backend Python : Triton supporte un backend Python plus simple que TensorRT
• Modèles alternatifs légers : phi3.5, qwen2.5:3b, mistral, tinyllama
■ Répartition des Rôles par Filière
■■ INFRA — L'Architecte du Système
Mission :
• Choisir et déployer un serveur d'inférence avec Phi-3.5-Financial (Ollama / Triton / Serveur maison)
• Rendre le serveur accessible à l'équipe DEV WEB (URL + port)
• Optimiser les performances (paramètres d'inférence, quantization)
Livrables :
• Serveur d'inférence opérationnel avec Phi-3.5-Financial
• Documentation de déploiement (choix technique justifié)
■ IA — Le Spécialiste Modèles
Mission :
• Validation et tests du modèle Phi-3.5-Financial
• Optimisation des paramètres d'inférence
• Fine-tuning LoRA d'un modèle médical avec le dataset fourni
• Tests de performance du modèle expérimental
Livrables :
• Modèle Phi-3.5-Financial validé et optimisé
• Modèle médical expérimental fine-tuné (LoRA)
■ DATA — L'Expert Données
Mission :
• Validation des données d'entrée pour Phi-3.5-Financial
• Tests de qualité des conversations
• Analyse et nettoyage du dataset médical
• Préparation des données pour le fine-tuning LoRA
• Validation de la qualité des conversations médicales
Livrables :
• Dataset médical préparé et nettoyé
• Rapport de qualité des données
■ CYBER — Le Responsable Sécurité
Mission :
• Audit de sécurité du déploiement (Ollama, Triton, ou serveur maison)
• Tests de robustesse du modèle Phi-3.5-Financial
• Validation de l'intégrité des réponses
• Tests de sécurité du modèle médical fine-tuné
• Vérification de l'absence de biais problématiques
Livrables :
• Tests de robustesse validés
■ DEV WEB — Le Développeur Interface
Mission :
• Développer une interface web de chat (obligatoire)
• Intégrer l'API du serveur d'inférence choisi par l'équipe INFRA
• Ollama : http://localhost:11434
• Triton : http://localhost:8000
• Serveur maison : URL communiquée par l'équipe INFRA
• Interface utilisateur intuitive pour tester le modèle
Livrables :
• Interface web complète et fonctionnelle
• Intégration API temps réel avec le serveur d'inférence de l'équipe
■ Architecture du Projet
techcorp-ai-chat/
■■■ tritton_server/ # Configuration Triton Inference Server
■■■ models/ # Modèle Phi-3.5-Financial
■■■ medical_dataset/ # Dataset pour fine-tuning médical expérimental
■■■ scripts/ # Scripts d'entraînement et de tests
■ Documentation & Ressources Utiles
• Déploiement rapide HuggingFace avec Triton : github.com/triton-inference-server/tutorials
• Dataset Médical : huggingface.co/datasets/ruslanmv/ai-medical-chatbot
■ Mission Finale
Votre objectif principal : Rendre le modèle Phi-3.5-Financial accessible via une interface chat
professionnelle — peu importe le serveur d'inférence choisi (Ollama, Triton, ou maison), l'interface est non
négociable. N'oubliez pas d'expérimenter sur le fine-tuning du modèle médical.
TechCorp compte sur vous pour finaliser ce projet. Explorez les fichiers laissés par l'équipe précédente, ils peuvent
contenir des informations utiles !