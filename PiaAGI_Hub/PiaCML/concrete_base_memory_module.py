from abc import ABC, abstractmethod # Keep to allow BaseMemoryModule to be imported
import uuid # For generating unique memory IDs

# Attempt to import BaseMemoryModule from the current directory
try:
    from .base_memory_module import BaseMemoryModule
except ImportError:
    # Fallback for scenarios where the relative import might fail (e.g., running script directly)
    # This assumes base_memory_module.py is in the python path or same directory
    from base_memory_module import BaseMemoryModule

class ConcreteBaseMemoryModule(BaseMemoryModule):
    """
    A basic, in-memory concrete implementation of the BaseMemoryModule interface.
    It uses a Python dictionary for storage. Each memory item is assigned a unique ID.
    """

    def __init__(self):
        self._storage = {}  # Internal dictionary to store memory items: {memory_id: {'info': information, 'ctx': context}}
        self._next_id = 0 # Simple counter for demo purposes if UUID is not preferred for some items.
        print("ConcreteBaseMemoryModule initialized - In-memory dictionary storage.")

    def store(self, information: dict, context: dict = None) -> str:
        """
        Stores information into the memory module. Assigns a unique ID to the memory.

        Args:
            information (dict): The data to be stored.
            context (dict, optional): Additional contextual information.

        Returns:
            str: The unique ID assigned to the stored memory item.
        """
        memory_id = str(uuid.uuid4())
        self._storage[memory_id] = {'id': memory_id, 'info': information, 'ctx': context or {}}
        print(f"ConcreteBaseMemoryModule: Stored item with ID {memory_id}")
        return memory_id

    def retrieve(self, query: dict, criteria: dict = None) -> list[dict]:
        """
        Retrieves information based on a query and/or criteria.
        - If 'id' is in the query, it retrieves by ID.
        - If 'concept' is in the query (within 'info'), it retrieves items matching that concept.
        - If 'match_context' is in criteria, it filters items based on context matching.
        - If query is empty and no context criteria, returns all stored items.
        - Otherwise, returns items matching any of the above.
        """
        print(f"ConcreteBaseMemoryModule: Retrieving with query: {query}, criteria: {criteria}")
        results = []

        # Initial check for empty query and no specific criteria
        if not query and not (criteria and 'match_context' in criteria):
            print("ConcreteBaseMemoryModule: Empty query and no context criteria, returning all items.")
            return list(self._storage.values())

        # ID-based query has highest precedence
        query_id = query.get('id')
        if query_id and query_id in self._storage:
            # If ID matches, this is usually the only result expected.
            # However, context criteria might still apply if specified.
            item = self._storage[query_id]
            match_context_criteria = criteria.get('match_context') if criteria else None
            if match_context_criteria:
                context_match = True
                if item.get('ctx'):
                    for key, value in match_context_criteria.items():
                        if item['ctx'].get(key) != value:
                            context_match = False
                            break
                else: # No context in item, cannot match context criteria
                    context_match = False
                if context_match:
                    results.append(item)
            else: # No context criteria, ID match is enough
                results.append(item)
            return results


        # Concept-based query or context-based filtering
        # If an ID query was processed and returned, this part might be skipped
        # unless we want to accumulate results from different query types (not typical for this model).

        # Iterate once through all items if not already returned by ID query.
        items_to_check = list(self._storage.values())

        query_concept = query.get('concept')
        match_context_criteria = criteria.get('match_context') if criteria else None

        if query_concept or match_context_criteria:
            for item_data in items_to_check:
                passes_concept_query = False
                if query_concept:
                    if item_data['info'].get('concept') == query_concept:
                        passes_concept_query = True
                else: # No concept query, so it implicitly passes this part of the check
                    passes_concept_query = True

                passes_context_criteria = False
                if match_context_criteria:
                    context_match = True
                    if item_data.get('ctx'):
                        for key, value in match_context_criteria.items():
                            if item_data['ctx'].get(key) != value:
                                context_match = False
                                break
                    else: # No context in item, cannot match context criteria
                        context_match = False
                    if context_match:
                        passes_context_criteria = True
                else: # No context criteria, so it implicitly passes this part of the check
                    passes_context_criteria = True

                # Item must pass both (if specified)
                if passes_concept_query and passes_context_criteria:
                    if item_data not in results: # Avoid duplicates if ID query was also somehow relevant
                         results.append(item_data)

            if results: # If any concept or context match found
                return results

        # Fallback for non-empty query that didn't match ID, concept, or context criteria
        if query: # but not (query_id or query_concept or match_context_criteria made it here)
             print(f"ConcreteBaseMemoryModule: Query {query} with criteria {criteria} did not match any items via ID, concept, or context.")
             return [] # Return empty if specific query fields or context don't match

        # If query was empty but there WERE context criteria that didn't match anything
        if not query and match_context_criteria and not results:
            print(f"ConcreteBaseMemoryModule: Context criteria {match_context_criteria} did not match any items.")
            return []

        # Should be covered by the first check, but as a safeguard:
        print(f"ConcreteBaseMemoryModule: Unhandled query/criteria case or no matches. Query: {query}, Criteria: {criteria}")
        return []


    def delete_memory(self, memory_id: str) -> bool:
        """
        Deletes a memory item by its unique ID.

        Args:
            memory_id (str): The unique ID of the memory item to delete.

        Returns:
            bool: True if deletion was successful, False otherwise (e.g., item not found).
        """
        if memory_id in self._storage:
            del self._storage[memory_id]
            print(f"ConcreteBaseMemoryModule: Deleted item with ID {memory_id}")
            return True
        print(f"ConcreteBaseMemoryModule: Item with ID {memory_id} not found for deletion.")
        return False

    def manage_capacity(self) -> None:
        """
        Placeholder for managing memory module's capacity.
        A real implementation might involve consolidating, archiving, or removing items.
        """
        print("ConcreteBaseMemoryModule: manage_capacity() called - Placeholder. No action taken.")
        # Example: if len(self._storage) > 1000: # Some arbitrary limit
        #     print("Capacity limit reached, implement actual management logic.")
        pass

    def handle_forgetting(self, strategy: str = 'default') -> None:
        """
        Placeholder for implementing forgetting mechanisms.
        Strategies could include decay, interference-based forgetting, etc.
        """
        print(f"ConcreteBaseMemoryModule: handle_forgetting() called with strategy '{strategy}' - Placeholder. No action taken.")
        pass

    def update_memory_decay(self, memory_id: str, decay_factor: float) -> None:
        """
        Placeholder for updating the decay factor of a specific memory.
        This would be relevant for forgetting mechanisms.
        """
        if memory_id in self._storage:
            # Assuming 'decay' could be a field in context or info
            # self._storage[memory_id]['ctx']['decay_factor'] = decay_factor
            print(f"ConcreteBaseMemoryModule: update_memory_decay() called for ID {memory_id} with factor {decay_factor} - Placeholder.")
        else:
            print(f"ConcreteBaseMemoryModule: update_memory_decay() - ID {memory_id} not found.")
        pass

    def find_similar_memories(self, query_embedding: list[float], top_n: int) -> list[dict]:
        """
        Placeholder for finding similar memories based on an embedding vector.
        Requires memories to be stored with or convertible to embeddings.
        """
        print(f"ConcreteBaseMemoryModule: find_similar_memories() called with embedding (first 3 dims): {query_embedding[:3]} for top {top_n} - Placeholder.")
        # Actual implementation would involve vector similarity search (e.g., cosine similarity)
        return []

    def get_status(self) -> dict:
        """
        Returns the current status of the memory module.
        """
        status = {
            'total_items': len(self._storage),
            'module_type': 'ConcreteBaseMemoryModule',
            'storage_engine': 'in-memory Python dictionary'
        }
        print(f"ConcreteBaseMemoryModule: Status: {status}")
        return status

if __name__ == '__main__':
    # Example Usage / Simple Test
    memory = ConcreteBaseMemoryModule()

    # Store some items
    item1_id = memory.store({'type': 'fact', 'concept': 'PiaAGI', 'detail': 'Is a framework.'}, {'source': 'manual_input'})
    item2_id = memory.store({'type': 'event', 'concept': 'System Startup', 'timestamp': '12345'}, {'source': 'internal_log'})
    item3_id = memory.store({'type': 'fact', 'concept': 'PiaAGI', 'detail': 'Focuses on cognitive architecture.'}, {'source': 'manual_input'})

    # Retrieve items
    print("\n--- Retrieving ---")
    print("Retrieve item1 by ID:", memory.retrieve({'id': item1_id}))
    print("Retrieve 'PiaAGI' concepts:", memory.retrieve({'concept': 'PiaAGI'}))
    print("Retrieve non-existent concept:", memory.retrieve({'concept': 'NonExistent'}))
    print("Retrieve with empty query (all):", memory.retrieve({}))


    # Get status
    print("\n--- Status ---")
    memory.get_status()

    # Delete an item
    print("\n--- Deleting ---")
    memory.delete_memory(item2_id)
    print("Try deleting again (should fail):", memory.delete_memory(item2_id))
    memory.get_status()

    # Call placeholder methods
    print("\n--- Placeholders ---")
    memory.manage_capacity()
    memory.handle_forgetting()
    memory.update_memory_decay(item1_id, 0.95)
    memory.find_similar_memories([0.1, 0.2, 0.3], 5)

    print("\nExample Usage Complete.")
