# Tasks - Simple Categorization Logic

## Task Breakdown

### 1. Set up prompt infrastructure and schemas
- [x] 1.1 Write tests for InboxItem, Categorization, and ItemGroup Pydantic models
- [x] 1.2 Implement base prompt schemas in prompts/schemas.py
- [x] 1.3 Create prompt package structure with __init__.py
- [x] 1.4 Write tests for prompt registration system
- [x] 1.5 Implement prompt discovery and registration mechanism
- [x] 1.6 Add FastMCP prompt decorator imports
- [x] 1.7 Verify all schema tests pass

### 2. Implement GTD static rule engine (server-side)
**Note: Following Decision D008, this provides static GTD methodology rules for MCP prompts, NOT intelligent analysis**
**Note: You can use python libraries rapidfuzz, rank_bm25 and sentence-transformers for text pattern matching. You can use them in combination **

- [x] 2.1 Write tests for GTD methodology constants and static patterns
  - Test GTD clarifying questions format and completeness
  - Test keyword pattern dictionaries structure
  - Test decision tree text generation
  - Test response schema validation helpers
- [x] 2.2 Implement GTD methodology questions and decision tree templates
  - Static GTD clarifying questions for prompt inclusion
  - Decision tree text templates for prompt context
  - Category validation rules and definitions
  - GTD phase indicators and workflow constants
- [x] 2.3 Write tests for simple keyword pattern matching
  - Test context keyword pattern dictionaries
  - Test pattern lookup functions
  - Test multiple pattern matching for overlapping contexts
  - Test pattern case-insensitivity
- [x] 2.4 Implement context keyword pattern dictionaries
  - Static keyword lists for each GTD context (@calls, @computer, etc.)
  - Simple pattern matching utilities (no LLM but ok to use python libraries rapidfuzz, rank_bm25 and sentence-transformers)
  - Context suggestion helpers based on keyword presence
  - Multiple context support for items matching several patterns
- [x] 2.5 Write tests for time/complexity indicator patterns
  - Test keyword patterns for quick tasks (2-minute rule hints)
    - Use `rapidfuzz.process.extract()` for fuzzy matching keywords with typo tolerance
    - Test threshold values (80-90) for "quick", "simple", "brief" variations
  - Test project complexity indicators
    - Use `spacy.matcher.Matcher` for linguistic patterns like [verb + noun] combinations
    - Test patterns: "implement system", "develop feature", "create architecture"
  - Test delegation/waiting patterns
    - Use `spacy` dependency parsing for "waiting on [PERSON]" structures
    - Use `rapidfuzz` for fuzzy matching delegation verbs: "assigned", "delegated", "asked"
  - Test pattern priority when multiple matches occur
    - Test conflict resolution (e.g., "quick implementation" = project wins over two-minute)
    - Use `textstat.flesch_reading_ease()` and word count as tiebreakers
  - Test time complexity estimation
    - Use `textstat.lexicon_count()` and `textstat.syllable_count()` for complexity scoring
    - Validate 2-minute rule estimation: <10 words + high readability = 2-minute task
- [x] 2.6 Implement static indicator pattern collections
  - Two-minute rule keyword indicators (quick, simple, brief, etc.)
    - Use `spacy.matcher.Matcher` for rule-based patterns: [{"LOWER": {"IN": ["quick", "simple", "brief"]}}]
    - Use `rapidfuzz.process.extract()` as fallback for fuzzy keyword matching (threshold: 85)
    - Include time indicators: "just a second", "real quick", "one minute"
  - Project complexity indicators (implement, develop, create, etc.)
    - Use `spacy` linguistic patterns: [{"LOWER": "implement"}, {"POS": "NOUN"}]
    - Use `textstat.flesch_reading_ease()` < 50 + word count > 20 as complexity signals
    - Pattern examples: "multi-step", "multi-phase", "research and develop"
  - Delegation patterns (waiting, pending, depends, etc.)
    - Use `spacy` dependency parsing for "waiting on [PERSON]" structures
    - Use `rapidfuzz` for delegation verb variations: "assigned" → "asigned", "delegated"
    - Include context patterns: "@mentions", "follow up with", "need approval from"
  - Priority/urgency keywords for prompt context
    - Use `spacy.matcher.PhraseMatcher` for exact phrase matching: "ASAP", "urgent", "critical"
    - Use `rapidfuzz` for deadline patterns: "due today" → "do today", "due tomorow"
    - Include temporal urgency: "EOD", "COB", "by end of week"
  - Create hybrid analyzer combining all approaches
    - GTDPatternAnalyzer class with configurable thresholds
    - Pattern priority system: priority > project > delegation > two-minute
    - Confidence scoring based on pattern strength and fuzzy match scores
- [ ] 2.7 Create GTD methodology documentation and constants
  - Document GTD decision tree logic for prompts
    - Include decision flowchart with pattern matching integration points
    - Document when to use spacy vs rapidfuzz vs textstat for each decision node
    - Create examples showing library combinations for edge cases
  - Define category descriptions and usage rules
    - Document pattern matching confidence thresholds for each GTD category
    - Include library-specific configuration examples (spacy model, rapidfuzz thresholds)
    - Create troubleshooting guide for pattern matching conflicts
  - Create context definitions and typical use cases
    - Map GTD contexts to pattern detection strategies (@calls → phone keywords + spacy patterns)
    - Document performance characteristics of each library approach
    - Include examples of hybrid detection (spacy + rapidfuzz for robustness)
  - Generate prompt template building utilities
    - Create utilities to convert pattern matching results into prompt context
    - Document how static patterns inform Claude's reasoning process
    - Include token optimization strategies for prompt efficiency
  - Create pattern matching strategy documentation
    - Performance benchmarks: spacy (linguistic) vs rapidfuzz (fuzzy) vs textstat (complexity)
    - Memory usage guidelines for en_core_web_sm model vs keyword-only approaches
    - Offline operation confirmation (no external API dependencies)
- [ ] 2.8 Verify all static rule engine tests pass
  - Integration tests with prompt generation
    - Test spacy pattern extraction feeds correctly into MCP prompt context
    - Validate rapidfuzz results integrate with prompt hints for Claude
    - Test textstat complexity scores inform prompt decision guidance
  - Validation of rule consistency
    - Use `hypothesis` for property-based testing of pattern matching edge cases
    - Test pattern conflict resolution with random text generation
    - Validate that spacy + rapidfuzz + textstat combinations produce consistent results
  - Performance tests for pattern matching
    - Benchmark spacy.matcher performance with 1000+ text samples
    - Test rapidfuzz.process.extract() speed with large keyword dictionaries
    - Measure textstat analysis time for varying text complexity
    - Validate sub-100ms response time for single text analysis
  - Coverage verification for all GTD methodology areas
    - Use `pytest-cov` to ensure >95% code coverage for pattern matching modules
    - Test all spacy pattern combinations (linguistic rules)
    - Test all rapidfuzz threshold configurations (fuzzy matching)
    - Test all textstat metrics integration (complexity scoring)
    - Property-based testing with `hypothesis.strategies.text()` for robustness
  - Library-specific robustness testing
    - Test spacy with malformed/non-English text (graceful degradation)
    - Test rapidfuzz with empty strings, special characters, and Unicode
    - Test textstat with edge cases (single words, very long texts)
    - Validate memory usage stays within acceptable bounds for MCP server

### 3. Create core MCP prompts (Claude Desktop intelligence)
**Note: These prompts use static rules from Task 2 to guide Claude Desktop's LLM reasoning**

- [ ] 3.1 Write tests for inbox_clarification prompt generation
  - Test prompt includes GTD decision tree from rule engine
  - Test clarifying questions integration from static rules
  - Test context pattern hints inclusion
  - Test project indicator guidance
- [ ] 3.2 Implement inbox_clarification prompt with GTD template
  - Include GTD methodology questions from rule engine
  - Add decision tree text from static rules
  - Include context keyword hints for Claude's reasoning
  - Reference project indicators for multi-step detection
  - Guide Claude through confidence assessment
- [ ] 3.3 Write tests for quick_categorize prompt
  - Test streamlined decision process
  - Test integration with static rule patterns
  - Test fallback to full clarification when needed
- [ ] 3.4 Implement quick_categorize for simple items
  - Lightweight prompt for obvious categorizations
  - Use subset of static patterns for speed
  - Include escalation logic for complex items
- [ ] 3.5 Write tests for batch_process_inbox prompt
  - Test batch consistency using same static rules
  - Test grouping logic guidance for Claude
  - Test processing up to 20 items efficiently
- [ ] 3.6 Implement batch_process_inbox with grouping logic
  - Guide Claude to identify similar patterns
  - Use static indicators for grouping suggestions
  - Maintain categorization consistency across batch
- [ ] 3.7 Test prompt response formatting and JSON structure
  - Validate schema compliance with existing Pydantic models
  - Test error handling for malformed Claude responses
  - Test response parsing and validation
- [ ] 3.8 Verify all prompt tests pass
  - Integration tests with static rule engine
  - End-to-end prompt generation and validation
  - Performance testing for prompt token efficiency

### 4. Add validation and error handling
- [ ] 4.1 Write tests for input validation functions
- [ ] 4.2 Implement inbox item validation and sanitization
  - Limit item length to 500 characters
  - Remove excessive whitespace
  - Handle empty or malformed items
- [ ] 4.3 Write tests for response validation
- [ ] 4.4 Implement categorization result validation
  - Verify required fields present
  - Validate category values
  - Check confidence levels
- [ ] 4.5 Write tests for error scenarios
- [ ] 4.6 Implement error handling with proper error codes
- [ ] 4.7 Verify all validation tests pass

### 5. Integrate prompts with MCP server
- [ ] 5.1 Write tests for prompt registration in server.py
- [ ] 5.2 Register all prompts with MCP server
  - Add inbox_clarification prompt
  - Add quick_categorize prompt
  - Add batch_process_inbox prompt
- [ ] 5.3 Write tests for prompt meta information
- [ ] 5.4 Add prompt discovery meta information
  - Include GTD phase indicators
  - Add usage frequency hints
  - Create categorization tags
- [ ] 5.5 Update server instructions with prompt usage
- [ ] 5.6 Test prompt invocation through MCP protocol
- [ ] 5.7 Verify all integration tests pass

### 6. Extend static pattern recognition (server-side)
**Note: Extends Task 2 with domain-specific keyword patterns for prompt hints**

- [ ] 6.1 Write tests for email keyword pattern detection
  - Test email-specific action keywords (reply, forward, send)
    - Use `spacy.matcher.Matcher` for verb-object patterns: [{"LOWER": "reply"}, {"LOWER": "to"}]
    - Use `rapidfuzz` for typo-tolerant email verbs: "reply" → "relpy", "respond" → "respnd"
    - Test email signature detection as context clue for @computer assignment
  - Test email context patterns (@computer required)
    - Use `spacy` to detect email headers/signatures as automatic @computer indicators
    - Test pattern: "From:", "To:", "Subject:" → automatically suggests @computer context
  - Test urgency indicators in email content
    - Use `rapidfuzz` for deadline variations: "EOD" → "end of day", "ASAP" → "as soon as possible"
    - Use `spacy` for temporal expressions: "by [TIME]", "before [DATE]"
- [ ] 6.2 Implement email-specific static keyword patterns
  - Email action verb patterns (reply, respond, send, forward)
    - Use `spacy.matcher.PhraseMatcher` for exact email action phrases
    - Use `rapidfuzz.process.extract()` with email-specific dictionary for fuzzy matching
    - Include variations: "get back to", "follow up with", "send update to"
  - Email urgency keywords (urgent, asap, deadline)
    - Use `spacy` for temporal pattern extraction: "due [DATE]", "by [TIME]"
    - Use `rapidfuzz` for urgency acronym variations: "ASAP", "asap", "a.s.a.p"
  - Email delegation patterns (cc, bcc, forward to)
    - Use `spacy` dependency parsing for "cc [PERSON]", "forward to [PERSON]" structures
    - Use `rapidfuzz` for delegation variations: "copy" → "cc", "send to" → "forward to"
- [ ] 6.3 Write tests for meeting note keyword patterns
  - Test meeting-specific keywords (discuss, agenda, follow-up)
    - Use `spacy.matcher.Matcher` for meeting structure patterns: [{"LOWER": "agenda"}, {"LOWER": "item"}]
    - Use `rapidfuzz` for meeting terminology variations: "follow-up" → "followup", "follow up"
    - Test bullet point detection as action item indicator using spacy tokenization
  - Test action item extraction patterns (action, todo, assign)
    - Use `spacy` dependency parsing for "assigned to [PERSON]" structures
    - Use `rapidfuzz` for action variations: "todo" → "to do", "to-do", "action item"
    - Test numbered/bulleted list detection as action context indicators
  - Test meeting context hints (@office, @calls for follow-ups)
    - Use pattern analysis: "call [PERSON]" → @calls, "schedule meeting" → @office
    - Use `spacy` for person name extraction to auto-suggest @calls context
- [ ] 6.4 Implement meeting note static keyword collections
  - Meeting action keywords (follow-up, schedule, prepare)
    - Use `spacy.matcher.Matcher` for meeting action patterns: [{"LOWER": "schedule"}, {"POS": "NOUN"}]
    - Use `rapidfuzz` for meeting action fuzzy matching with high confidence threshold (90+)
    - Include temporal meeting patterns: "next week", "by Friday", "before the deadline"
  - Meeting outcome patterns (decided, agreed, action item)
    - Use `spacy` for decision pattern extraction: "decided to", "agreed that", "action item:"
    - Use `rapidfuzz` for outcome terminology: "decision" → "decided", "agreement" → "agreed"
  - Meeting delegation keywords (assigned to, responsible for)
    - Use `spacy` dependency parsing for delegation structures with person entities
    - Use `rapidfuzz` for delegation variations: "responsible" → "responsible for", "owns"
- [ ] 6.5 Write tests for delegation keyword patterns
  - Test waiting-for indicators (waiting, pending, depends on)
    - Use `spacy.matcher.Matcher` for dependency patterns: [{"LOWER": "waiting"}, {"LOWER": "for"}]
    - Use `rapidfuzz` for waiting variations: "pending" → "pending on", "blocked" → "blocked by"
    - Test temporal waiting patterns: "waiting until", "pending approval from"
  - Test delegation verbs (assigned, delegated, asked)
    - Use `spacy` dependency parsing for delegation with person extraction
    - Use `rapidfuzz` for delegation verb variations: "assigned" → "asigned", "delegated" → "handed off"
    - Test passive voice detection: "was asked to" vs "asked [PERSON] to"
  - Test person name extraction hints for prompts
    - Use `spacy.ents` for PERSON entity recognition in delegation contexts
    - Use `rapidfuzz` for name variations and nicknames in follow-up patterns
    - Test @mention pattern detection as person indicators
- [ ] 6.6 Implement delegation detection keyword patterns
  - Waiting-for trigger words (waiting, pending, blocked by)
    - Use `spacy.matcher.Matcher` for complex waiting patterns with dependency structure
    - Use `rapidfuzz` for status variations: "pending" → "awaiting", "blocked" → "stuck on"
    - Include escalation patterns: "overdue from", "follow up with"
  - Delegation action verbs (asked, assigned, delegated, requested)
    - Use `spacy` for verb-person-action parsing: "asked [PERSON] to [ACTION]"
    - Use `rapidfuzz` for delegation synonyms: "assigned" → "given to", "handed off"
    - Test delegation confidence scoring based on pattern strength
  - Follow-up reminder keywords (check, follow up, remind)
    - Use `spacy.matcher.Matcher` for follow-up action patterns
    - Use `rapidfuzz` for reminder variations: "check in" → "check up", "follow up" → "followup"
    - Include temporal follow-up patterns: "remind me in", "check back"
- [ ] 6.7 Create extensible static pattern system
  - Pattern category framework for new domains
    - Design plugin architecture for domain-specific pattern libraries
    - Use `pydantic` for pattern configuration validation and type safety
    - Create abstract pattern classes that combine spacy + rapidfuzz + textstat
  - Priority ordering for overlapping pattern matches
    - Implement weighted scoring system combining pattern confidence and domain relevance
    - Use pattern hierarchy: exact spacy matches > fuzzy rapidfuzz > textstat metrics
    - Create conflict resolution with configurable precedence rules
  - Pattern composition utilities for prompt building
    - Create utilities to aggregate pattern results into structured prompt context
    - Implement pattern-to-prompt-hint conversion for Claude guidance
    - Include confidence aggregation and uncertainty indication for prompts
- [ ] 6.8 Verify all pattern recognition tests pass
  - Integration with core rule engine (Task 2)
    - Test domain-specific patterns integrate cleanly with base GTD patterns
    - Validate pattern library loading and configuration management
    - Test pattern conflict resolution across domains (email vs meeting vs delegation)
  - Performance testing for large pattern sets
    - Benchmark combined spacy + rapidfuzz + textstat performance with 10k+ patterns
    - Test memory usage with multiple domain pattern libraries loaded
    - Validate sub-200ms response time for complex pattern analysis
  - Validation of pattern precedence rules
    - Test edge cases where multiple patterns match with similar confidence
    - Use `hypothesis` for property-based testing of pattern conflict resolution
    - Validate that higher-priority patterns consistently override lower-priority ones

### 7. Integration testing and documentation
- [ ] 7.1 Test single item categorization workflow
  - Invoke inbox_clarification with one item
  - Verify correct GTD category suggestion
  - Validate reasoning and confidence
- [ ] 7.2 Test batch processing workflow with 20 items
  - Create diverse test items
  - Verify grouping suggestions
  - Validate consistent categorization
- [ ] 7.3 Test project association workflow
  - Provide existing projects list
  - Verify items linked to relevant projects
  - Validate new project suggestions
- [ ] 7.4 Test context assignment workflow
  - Test prompts provide context keyword hints to Claude
  - Verify Claude receives static pattern guidance
  - Validate context suggestions in Claude's responses
- [ ] 7.5 Test quick categorization performance
  - Measure response time < 2 seconds
  - Verify minimal token usage
  - Validate accuracy for simple items
- [ ] 7.6 Test error recovery scenarios
  - Test with malformed JSON responses
  - Test with timeout scenarios
  - Verify graceful degradation
- [ ] 7.7 Write user documentation with GTD primer
  - Explain GTD methodology basics
  - Provide prompt usage examples
  - Create troubleshooting guide
- [ ] 7.8 Write API documentation
  - Document all prompt schemas
  - Provide response examples
  - Create integration guide
- [ ] 7.9 Create example workflows
  - Daily inbox processing
  - Weekly review preparation
  - Project planning session
- [ ] 7.10 Performance optimization
  - Minimize prompt token usage
  - Implement response caching
  - Optimize for Claude's context window

## Architecture Notes

**Key Change from Original Plan**: Following Decision D008 analysis, Tasks 2 and 6 now implement **static keyword patterns and GTD methodology rules** (server-side) rather than intelligent text analysis. The actual intelligence happens in Claude Desktop via MCP prompts (Task 3) that reference these static rules.

**Server-Side (No LLM)**: Static patterns, keyword lists, GTD methodology constants, validation rules
**Client-Side (Claude Desktop)**: Natural language understanding, confidence assessment, intelligent categorization

## Task Dependencies

- Task 1 must complete before Tasks 2 and 3 (foundational schemas)
- Task 2 can proceed independently after Task 1 (static rules only)
- Task 3 depends on Tasks 1 and 2 (needs schemas and static rules for prompt generation)
- Task 4 can proceed in parallel with Task 3
- Task 5 depends on Task 3 (needs prompts to register)
- Task 6 can proceed independently after Task 2 (extends static patterns)
- Task 7 depends on all previous tasks (final integration)

## Estimated Complexity (Revised)

- **Task 1**: Low complexity (2-3 hours) - Pydantic schemas and structure
- **Task 2**: Low-Medium complexity (2-3 hours) - Static GTD rules and patterns (simplified from intelligent analysis)
- **Task 3**: High complexity (5-6 hours) - Core prompt implementation with static rule integration
- **Task 4**: Medium complexity (2-3 hours) - Validation layer
- **Task 5**: Low complexity (2-3 hours) - Server integration
- **Task 6**: Low-Medium complexity (2-3 hours) - Static pattern extensions (simplified from intelligent analysis)
- **Task 7**: High complexity (6-8 hours) - Comprehensive testing and documentation

**Total Estimate**: 21-29 hours of development time (reduced due to simpler static approach)

## Success Criteria

- ✅ All prompts properly registered with MCP server
- ✅ 90% accurate categorization for standard inbox items
- ✅ Response time < 2 seconds for single item processing
- ✅ Batch processing handles 20 items efficiently
- ✅ Zero API key configuration required
- ✅ Clear explanations provided for all categorizations
- ✅ GTD methodology properly implemented
- ✅ All tests passing with >90% code coverage
