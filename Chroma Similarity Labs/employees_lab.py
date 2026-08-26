"""
Lab 2 — Employee similarity search + metadata filters (Chroma + MiniLM).
"""

from __future__ import annotations

from chroma_utils import create_collection

EMPLOYEES = [
    {
        "id": "employee_1",
        "name": "John Doe",
        "experience": 5,
        "department": "Engineering",
        "role": "Software Engineer",
        "skills": "Python, JavaScript, React, Node.js, databases",
        "location": "New York",
        "employment_type": "Full-time",
    },
    {
        "id": "employee_2",
        "name": "Jane Smith",
        "experience": 8,
        "department": "Marketing",
        "role": "Marketing Manager",
        "skills": "Digital marketing, SEO, content strategy, analytics, social media",
        "location": "Los Angeles",
        "employment_type": "Full-time",
    },
    {
        "id": "employee_3",
        "name": "Alice Johnson",
        "experience": 3,
        "department": "HR",
        "role": "HR Coordinator",
        "skills": "Recruitment, employee relations, HR policies, training programs",
        "location": "Chicago",
        "employment_type": "Full-time",
    },
    {
        "id": "employee_4",
        "name": "Michael Brown",
        "experience": 12,
        "department": "Engineering",
        "role": "Senior Software Engineer",
        "skills": "Java, Spring Boot, microservices, cloud architecture, DevOps",
        "location": "San Francisco",
        "employment_type": "Full-time",
    },
    {
        "id": "employee_5",
        "name": "Emily Wilson",
        "experience": 2,
        "department": "Marketing",
        "role": "Marketing Assistant",
        "skills": "Content creation, email marketing, market research, social media management",
        "location": "Austin",
        "employment_type": "Part-time",
    },
    {
        "id": "employee_6",
        "name": "David Lee",
        "experience": 15,
        "department": "Engineering",
        "role": "Engineering Manager",
        "skills": "Team leadership, project management, software architecture, mentoring",
        "location": "Seattle",
        "employment_type": "Full-time",
    },
    {
        "id": "employee_7",
        "name": "Sarah Clark",
        "experience": 8,
        "department": "HR",
        "role": "HR Manager",
        "skills": "Performance management, compensation planning, policy development, conflict resolution",
        "location": "Boston",
        "employment_type": "Full-time",
    },
    {
        "id": "employee_8",
        "name": "Chris Evans",
        "experience": 20,
        "department": "Engineering",
        "role": "Senior Architect",
        "skills": "System design, distributed systems, cloud platforms, technical strategy",
        "location": "New York",
        "employment_type": "Full-time",
    },
    {
        "id": "employee_9",
        "name": "Jessica Taylor",
        "experience": 4,
        "department": "Marketing",
        "role": "Marketing Specialist",
        "skills": "Brand management, advertising campaigns, customer analytics, creative strategy",
        "location": "Miami",
        "employment_type": "Full-time",
    },
    {
        "id": "employee_10",
        "name": "Alex Rodriguez",
        "experience": 18,
        "department": "Engineering",
        "role": "Lead Software Engineer",
        "skills": "Full-stack development, React, Python, machine learning, data science",
        "location": "Denver",
        "employment_type": "Full-time",
    },
    {
        "id": "employee_11",
        "name": "Hannah White",
        "experience": 6,
        "department": "HR",
        "role": "HR Business Partner",
        "skills": "Strategic HR, organizational development, change management, employee engagement",
        "location": "Portland",
        "employment_type": "Full-time",
    },
    {
        "id": "employee_12",
        "name": "Kevin Martinez",
        "experience": 10,
        "department": "Engineering",
        "role": "DevOps Engineer",
        "skills": "Docker, Kubernetes, AWS, CI/CD pipelines, infrastructure automation",
        "location": "Phoenix",
        "employment_type": "Full-time",
    },
    {
        "id": "employee_13",
        "name": "Rachel Brown",
        "experience": 7,
        "department": "Marketing",
        "role": "Marketing Director",
        "skills": "Strategic marketing, team leadership, budget management, campaign optimization",
        "location": "Atlanta",
        "employment_type": "Full-time",
    },
    {
        "id": "employee_14",
        "name": "Matthew Garcia",
        "experience": 3,
        "department": "Engineering",
        "role": "Junior Software Engineer",
        "skills": "JavaScript, HTML/CSS, basic backend development, learning frameworks",
        "location": "Dallas",
        "employment_type": "Full-time",
    },
    {
        "id": "employee_15",
        "name": "Olivia Moore",
        "experience": 12,
        "department": "Engineering",
        "role": "Principal Engineer",
        "skills": "Technical leadership, system architecture, performance optimization, mentoring",
        "location": "San Francisco",
        "employment_type": "Full-time",
    },
]


def _employee_document(employee: dict) -> str:
    doc = (
        f"{employee['role']} with {employee['experience']} years of experience "
        f"in {employee['department']}. "
    )
    doc += f"Skills: {employee['skills']}. Located in {employee['location']}. "
    doc += f"Employment type: {employee['employment_type']}."
    return doc


def main() -> None:
    try:
        collection = create_collection(
            "employee_collection",
            description="A collection for storing employee data",
        )
        print(f"Collection created: {collection.name}")

        documents = [_employee_document(e) for e in EMPLOYEES]
        collection.add(
            ids=[e["id"] for e in EMPLOYEES],
            documents=documents,
            metadatas=[
                {
                    "name": e["name"],
                    "department": e["department"],
                    "role": e["role"],
                    "experience": e["experience"],
                    "location": e["location"],
                    "employment_type": e["employment_type"],
                }
                for e in EMPLOYEES
            ],
        )

        all_items = collection.get()
        print(f"Documents in collection: {len(all_items['documents'])}")

        print("\n=== Similarity Search ===")
        print("\n1. Python developers:")
        q = "Python developer with web development experience"
        results = collection.query(query_texts=[q], n_results=3)
        print(f"Query: '{q}'")
        for i, (doc_id, document, distance) in enumerate(
            zip(results["ids"][0], results["documents"][0], results["distances"][0])
        ):
            meta = results["metadatas"][0][i]
            print(f"  {i + 1}. {meta['name']} ({doc_id}) - Distance: {distance:.4f}")
            print(f"     Role: {meta['role']}, Department: {meta['department']}")
            print(f"     Document: {document[:100]}...")

        print("\n2. Leadership / management:")
        q = "team leader manager with experience"
        results = collection.query(query_texts=[q], n_results=3)
        print(f"Query: '{q}'")
        for i, (doc_id, _, distance) in enumerate(
            zip(results["ids"][0], results["documents"][0], results["distances"][0])
        ):
            meta = results["metadatas"][0][i]
            print(f"  {i + 1}. {meta['name']} ({doc_id}) - Distance: {distance:.4f}")
            print(f"     Role: {meta['role']}, Experience: {meta['experience']} years")

        print("\n=== Metadata Filtering ===")
        print("\n3. Engineering employees:")
        results = collection.get(where={"department": "Engineering"})
        print(f"Found {len(results['ids'])}:")
        for i, _ in enumerate(results["ids"]):
            meta = results["metadatas"][i]
            print(f"  - {meta['name']}: {meta['role']} ({meta['experience']} years)")

        print("\n4. 10+ years experience:")
        results = collection.get(where={"experience": {"$gte": 10}})
        print(f"Found {len(results['ids'])}:")
        for i, _ in enumerate(results["ids"]):
            meta = results["metadatas"][i]
            print(f"  - {meta['name']}: {meta['role']} ({meta['experience']} years)")

        print("\n5. California (SF / LA):")
        results = collection.get(
            where={"location": {"$in": ["San Francisco", "Los Angeles"]}}
        )
        print(f"Found {len(results['ids'])}:")
        for i, _ in enumerate(results["ids"]):
            meta = results["metadatas"][i]
            print(f"  - {meta['name']}: {meta['location']}")

        print("\n=== Combined: Similarity + Filters ===")
        print("\n6. Senior Python / full-stack in major tech cities:")
        q = "senior Python developer full-stack"
        results = collection.query(
            query_texts=[q],
            n_results=5,
            where={
                "$and": [
                    {"experience": {"$gte": 8}},
                    {"location": {"$in": ["San Francisco", "New York", "Seattle"]}},
                ]
            },
        )
        print(f"Query: '{q}' with filters (8+ years, major tech cities)")
        if not results["ids"][0]:
            print("No matching employees.")
            return
        print(f"Found {len(results['ids'][0])}:")
        for i, (doc_id, document, distance) in enumerate(
            zip(results["ids"][0], results["documents"][0], results["distances"][0])
        ):
            meta = results["metadatas"][0][i]
            print(f"  {i + 1}. {meta['name']} ({doc_id}) - Distance: {distance:.4f}")
            print(
                f"     {meta['role']} in {meta['location']} "
                f"({meta['experience']} years)"
            )
            print(f"     Snippet: {document[:80]}...")
    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
