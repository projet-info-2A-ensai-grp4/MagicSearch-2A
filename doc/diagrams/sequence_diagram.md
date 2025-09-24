```mermaid
sequenceDiagram
    participant U as User
    participant C as Controller Layer
    participant S as Service Layer
    participant API as External Embedding API
    participant D as DAO
    participant P as Persistent Layer (DB)

    U->>C: Calls endpoint with natural language search
    C->>S: Forwards search request

    %% Vectorization via external API
    S->>API: Sends text for vectorization
    API-->>S: Returns embedded vectors

    %% Persistence of vectors
    S->>D: Requests to import vectors with ID
    D->>P: INSERT vectors into database
    P-->>D: Ack insert
    D-->>S: Confirmation

    %% Cosine similarity computation
    S->>S: Computes cosine similarity
    S->>S: Identifies ID of best vector

    %% Retrieval of the final map
    S->>D: Requests map by ID
    D->>P: SELECT map WHERE id = bestId
    P-->>D: Returns map
    D-->>S: Complete map
    S-->>C: Complete map
    C-->>U: Final response (map)
