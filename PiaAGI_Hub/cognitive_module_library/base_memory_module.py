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
    def store(self, information: dict, context: dict = None) -> bool:
        """
        Stores information into the memory module.

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
            bool: True if storage was successful, False otherwise.
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
            self.storage = {}
            self.item_id_counter = 0
            print("ConceptualLTM initialized - A very simplified LTM concept.")

        def store(self, information: dict, context: dict = None) -> bool:
            print(f"ConceptualLTM: Attempting to store: {information} with context: {context}")
            self.item_id_counter += 1
            self.storage[self.item_id_counter] = {'info': information, 'ctx': context or {}}
            print(f"ConceptualLTM: Stored item with ID {self.item_id_counter}")
            return True

        def retrieve(self, query: dict, criteria: dict = None) -> list[dict]:
            print(f"ConceptualLTM: Attempting to retrieve based on query: {query} and criteria: {criteria}")
            results = []
            # Highly simplified retrieval: exact match on a 'concept' in information
            if 'concept' in query:
                for item_id, stored_item in self.storage.items():
                    if stored_item['info'].get('concept') == query['concept']:
                        results.append(stored_item['info'])
            print(f"ConceptualLTM: Found {len(results)} items.")
            return results

        def manage_capacity(self) -> None:
            print("ConceptualLTM: manage_capacity() called. In a real system, this would involve complex processes.")
            if len(self.storage) > 10: # Arbitrary small capacity for demo
                print("ConceptualLTM: Capacity potentially exceeded. Forgetting oldest item for demo.")
                if self.storage:
                    oldest_item_id = min(self.storage.keys())
                    del self.storage[oldest_item_id]
                    print(f"ConceptualLTM: Forgot item with ID {oldest_item_id}")


        def handle_forgetting(self, strategy: str = 'default') -> None:
            print(f"ConceptualLTM: handle_forgetting() called with strategy: {strategy}")
            # This would be a complex mechanism in a real LTM.
            pass

        def get_status(self) -> dict:
            status = {
                'capacity_percentage': (len(self.storage) / 10.0) * 100 if 10 > 0 else 0, # Conceptual capacity of 10 items
                'total_items': len(self.storage),
                'module_type': 'ConceptualLTM'
            }
            print(f"ConceptualLTM: Status: {status}")
            return status

    # Conceptual usage demonstration:
    ltm_instance = ConceptualLTM()
    ltm_instance.store({'type': 'semantic', 'concept': 'Dark Matter', 'definition': 'Hypothetical matter not interacting with light.'}, {'source': 'user_input'})
    ltm_instance.store({'type': 'semantic', 'concept': 'AGI', 'definition': 'Artificial General Intelligence.'})
    retrieved_info = ltm_instance.retrieve({'concept': 'Dark Matter'})
    print(f"Retrieved from LTM: {retrieved_info}")
    ltm_instance.get_status()
    ltm_instance.manage_capacity() # Potentially forget if capacity is small and exceeded
