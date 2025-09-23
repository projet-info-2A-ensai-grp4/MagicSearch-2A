sequenceDiagram
    participant U as User
    participant C as Controller Layer
    participant S as Service Layer
    participant API as External Embedding API
    participant D as DAO
    participant P as Persistent Layer (DB)
    U->>C: Appelle endpoint avec recherche en langage naturel
    C->>S: Transmet la requête de recherche
    %% Vectorisation via API externe
    S->>API: Envoie texte pour vectorisation
    API-->>S: Retourne vecteurs embed
    %% Persistance des vecteurs
    S->>D: Demande d'importer vecteurs avec ID
    D->>P: INSERT vecteurs en base
    P-->>D: Ack insert
    D-->>S: Confirmation
    %% Calcul du cosine similarity
    S->>S: Calcule similarité cosinus
    S->>S: Identifie l'ID du meilleur vecteur
    %% Récupération de la carte finale
    S->>D: Demande carte par ID
    D->>P: SELECT carte WHERE id = bestId
    P-->>D: Retourne carte
    D-->>S: Carte complète
    S-->>C: Carte complète
    C-->>U: Réponse finale (carte)
