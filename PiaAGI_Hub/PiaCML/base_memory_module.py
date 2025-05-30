from abc import ABC, abstractmethod

class BaseMemoryModule(ABC):
    """
    Abstract Base Class for all memory modules within the PiaAGI Cognitive Architecture.

    This class defines the common interface that all memory components (e.g., LTM, WM, Sensory Memory)
    should adhere to, ensuring a consistent way for the AGI to interact with its memory systems.
    The specific implementation of these methods will vary greatly depending on the type of memory
    and the chosen computational model.

    Refer to PiaAGI.md Sections 3.1.1 (Memory Systems) and 4.1.3 (Long-Term Memory Module)
    and 4.1.2 (Working Memory Module) for more context.
    """

    @abstractmethod
    def store(self, information: dict, context: dict = None) -> str:
        """
        Stores information into the memory module and returns a unique identifier for the stored item.

        The 'information' itself is expected to be a structured dict, but its exact content
        will depend on the type of memory (e.g., semantic fact, episodic event, procedural skill).
        'context' provides additional metadata (e.g., timestamp, emotional valence, source)
        that can be crucial for retrieval and memory management.

        Args:
            information (dict): The data to be stored. Structure depends on memory type.
                                Example for a semantic memory:
                                {'type': 'semantic', 'concept': 'PiaAGI', 'relation': 'is_a', 'value': 'cognitive_architecture'}
                                Example for an episodic memory:
                                {'type': 'episode', 'event': 'user_greeted', 'timestamp': 12345.67, 'actors': ['user', 'self']}
            context (dict, optional): Additional contextual information about the information being stored.
                                      This can include temporal tags, emotional tags, source, relevance, etc.
                                      Example: {'timestamp': 1234567890.0, 'source': 'PerceptionModule', 'emotion_valence': 0.7}

        Returns:
            str: A unique identifier for the stored memory item.
        """
        pass

    @abstractmethod
    def retrieve(self, query: dict, criteria: dict = None) -> list[dict]:
        """
        Retrieves information from the memory module based on a query and criteria.

        The 'query' specifies what information is being sought.
        'criteria' can refine the search (e.g., recency, relevance, emotional match).

        Args:
            query (dict): The query specifying the information to retrieve.
                          Example: {'concept': 'PiaAGI', 'relation': 'is_a'}
                          Example: {'event_type': 'user_interaction', 'last_n': 5}
            criteria (dict, optional): Additional criteria to guide the retrieval process.
                                       Example: {'min_relevance': 0.8, 'max_recency_days': 7, 'match_emotion': 'positive'}

        Returns:
            list[dict]: A list of information items matching the query and criteria.
                        Each item is a dict, similar in structure to what was stored.
                        Returns an empty list if no information is found.
        """
        pass

    @abstractmethod
    def delete_memory(self, memory_id: str) -> bool:
        """
        Deletes a memory item by its unique ID.

        Args:
            memory_id (str): The unique ID of the memory item to delete.

        Returns:
            bool: True if deletion was successful, False otherwise (e.g., item not found).
        """
        pass

    @abstractmethod
    def manage_capacity(self) -> None:
        """
        Manages the memory module's capacity.

        This can involve processes like consolidating less important information,
        archiving old data, or other strategies to prevent overload, depending on
        the memory type (e.g., WM has very limited capacity, LTM is vast but might
        still need optimization).

        This method might be called periodically by the AGI's Central Executive or
        triggered by internal state (e.g., high cognitive load in WM).
        """
        pass

    @abstractmethod
    def handle_forgetting(self, strategy: str = 'default') -> None:
        """
        Implements forgetting mechanisms to remove or weaken irrelevant or outdated information.

        Forgetting is crucial for adaptive intelligence, preventing interference and
        keeping knowledge relevant. Strategies could include decay over time,
        interference-based forgetting, or targeted removal based on utility.

        Args:
            strategy (str, optional): Specifies the forgetting strategy to apply.
                                      Examples: 'decay', 'interference_pruning', 'utility_based'.
                                      Defaults to 'default'.
        """
        pass

    @abstractmethod
    def get_status(self) -> dict:
        """
        Returns the current status of the memory module.

        This could include information like current capacity usage, number of items,
        average retrieval time, health metrics, etc. Useful for the Self-Model
        and for debugging or analysis.

        Returns:
            dict: A dictionary containing status information.
                  Example: {'capacity_percentage': 65.5, 'total_items': 1500000, 'last_accessed': 'timestamp'}
        """
        pass

if __name__ == '__main__':
    # This section is for conceptual illustration and won't be run directly by other modules.
    # It shows how one might conceptually think about a concrete implementation,
    # though BaseMemoryModule itself cannot be instantiated.

    class ConceptualLTM(BaseMemoryModule):
        def __init__(self):
            self.storage = {} # Stores items by string ID now
            self.item_id_counter = 0 # Used to generate unique IDs
            print("ConceptualLTM initialized - A very simplified LTM concept.")

        def store(self, information: dict, context: dict = None) -> str:
            print(f"ConceptualLTM: Attempting to store: {information} with context: {context}")
            self.item_id_counter += 1
            memory_id = str(self.item_id_counter) # Generate string ID
            self.storage[memory_id] = {'id': memory_id, 'info': information, 'ctx': context or {}}
            print(f"ConceptualLTM: Stored item with ID {memory_id}")
            return memory_id # Return the string ID

        def retrieve(self, query: dict, criteria: dict = None) -> list[dict]:
            print(f"ConceptualLTM: Attempting to retrieve based on query: {query} and criteria: {criteria}")
            results = []
            if not query:
                return list(self.storage.values())
            
            query_id = query.get('id')
            if query_id and query_id in self.storage:
                return [self.storage[query_id]]

            if 'concept' in query:
                for item_id, stored_item in self.storage.items():
                    if stored_item['info'].get('concept') == query['concept']:
                        results.append(stored_item) # Append the whole item including its ID
            print(f"ConceptualLTM: Found {len(results)} items.")
            return results
        
        def delete_memory(self, memory_id: str) -> bool:
            print(f"ConceptualLTM: Attempting to delete item with ID {memory_id}")
            if memory_id in self.storage:
                del self.storage[memory_id]
                print(f"ConceptualLTM: Deleted item with ID {memory_id}")
                return True
            print(f"ConceptualLTM: Item with ID {memory_id} not found for deletion.")
            return False

        def manage_capacity(self) -> None:
            print("ConceptualLTM: manage_capacity() called. In a real system, this would involve complex processes.")
            # Example: if len(self.storage) > 10: # Arbitrary small capacity for demo
            #     print("ConceptualLTM: Capacity potentially exceeded. Forgetting oldest item for demo.")
            #     if self.storage:
            #         # Deletion now requires string IDs
            #         oldest_item_id = min(self.storage.keys(), key=lambda k: self.storage[k].get('ctx', {}).get('timestamp', float('inf'))) # Example: find oldest by timestamp
            #         self.delete_memory(oldest_item_id)
            pass # Simplified for this example


        def handle_forgetting(self, strategy: str = 'default') -> None:
            print(f"ConceptualLTM: handle_forgetting() called with strategy: {strategy}")
            # This would be a complex mechanism in a real LTM.
            pass

        def get_status(self) -> dict:
            status = {
                'capacity_percentage': (len(self.storage) / 100.0) * 100, # Conceptual capacity of 100 items
                'total_items': len(self.storage),
                'module_type': 'ConceptualLTM'
            }
            print(f"ConceptualLTM: Status: {status}")
            return status

    # Conceptual usage demonstration:
    ltm_instance = ConceptualLTM()
    id1 = ltm_instance.store({'type': 'semantic', 'concept': 'Dark Matter', 'definition': 'Hypothetical matter...'}, {'source': 'user_input', 'timestamp': 1})
    id2 = ltm_instance.store({'type': 'semantic', 'concept': 'AGI', 'definition': 'Artificial General Intelligence.'}, {'timestamp': 2})
    
    print("\nRetrieving AGI by ID:", ltm_instance.retrieve({'id': id2}))
    print("Retrieving Dark Matter concepts:", ltm_instance.retrieve({'concept': 'Dark Matter'}))
    
    ltm_instance.get_status()
    
    print("\nDeleting Dark Matter (ID:", id1, ")")
    ltm_instance.delete_memory(id1)
    print("Try deleting Dark Matter again (should fail):", ltm_instance.delete_memory(id1))
    
    ltm_instance.get_status()
    ltm_instance.manage_capacity()
