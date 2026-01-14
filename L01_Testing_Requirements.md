# Testing Requirements - ILP Pronunciation Portal

## 1. System-level requirements

### a) The system must authenticate users correctly and issue valid JWT tokens upon successful login

**i. Level:** Since this requirement constrains the observable behaviour of the whole system, which requires the cooperation of authentication routes, security services, and database models, this is a system-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement comes with natural partitions: valid credentials with correct email and password, invalid email but valid password format, valid email but incorrect password, missing credentials, and malformed input. Category-partition testing explicitly asks us to identify and define such category partitions.
2. From those partitions, we can derive a systematic set of test scenarios that verify the system correctly authenticates users and rejects invalid attempts while issuing proper JWT tokens for successful logins.
3. Pairwise testing is not suitable here since the configuration parameters (email and password) are dependent on each other and must be tested in combination. Catalogue-based testing would require an established catalogue of authentication patterns which would be excessive for this requirement.

### b) The system must correctly validate user roles and enforce role-based access control

**i. Level:** Since this requirement constrains the observable behaviour of the whole system across multiple endpoints requiring different role permissions, this is a system-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement naturally partitions into scenarios: student accessing student-only endpoints, teacher accessing teacher-only endpoints, student attempting to access teacher endpoints (should be denied), teacher attempting to access student endpoints, and unauthenticated users attempting to access protected endpoints.
2. Category-partition testing allows us to systematically verify that each role can access appropriate endpoints and is denied access to restricted ones.
3. Pairwise testing would add overhead without benefit since we need to test all combinations of roles and endpoint types. Catalogue-based testing is not appropriate for this requirement.

### c) The system must accept only valid audio file formats when students submit pronunciation recordings

**i. Level:** Since this requirement constrains the observable behaviour of the whole system for audio file uploads, which requires cooperation between API routes, file handling, and validation logic, this is a system-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement comes with clear partitions: valid audio formats (WAV, MP3, WebM), invalid file formats (PDF, JPG, TXT), corrupted audio files, and extremely large files that might exceed limits.
2. Category-partition testing allows us to verify that the system accepts valid audio formats and rejects invalid ones with appropriate error messages.
3. Pairwise testing is not suitable because there's only one configuration parameter (file type and validity). Catalogue-based testing is not necessary here.

### d) The system must calculate student progress statistics accurately including words practiced, average score, total attempts, and streak count

**i. Level:** Since this requirement constrains the observable behaviour of the whole system for progress tracking, which requires cooperation between API routes, database queries, and calculation logic across multiple tables, this is a system-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement can be partitioned based on student activity patterns: student with no recordings, student with recordings on consecutive days (streak), student with recordings on non-consecutive days (no streak), student with multiple recordings on the same day, student with recordings over different time periods (week vs month).
2. Category-partition testing allows us to verify that statistics are calculated correctly across different usage patterns.
3. Pairwise testing would be unnecessarily complex since the partitions are based on temporal patterns of student activity. Catalogue-based testing is not applicable here.

### e) The system must ensure pronunciation assessment scores are within valid ranges (0-100)

**i. Level:** Since this requirement constrains the observable behaviour of the whole system for pronunciation assessment, which requires cooperation between the API, Azure Speech Service integration, and mock service fallback, this is a system-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Black-box testing

**iv. Appropriateness:**
1. This requirement does not depend on configuration variables and has clear boundary conditions. A simple black-box test that examines whether all scores (pronunciation_score, accuracy_score, fluency_score, completeness_score) fall within 0-100 range is sufficient.
2. The test should verify both Azure Speech Service results and mock assessment results to ensure consistency.

### f) The system must automatically generate feedback and assign grades based on pronunciation assessment results

**i. Level:** Since this requirement constrains the observable behaviour of the whole system for automatic feedback generation, which requires cooperation between pronunciation assessment, feedback service, and database recording, this is a system-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement can be partitioned based on score ranges that correspond to different feedback tiers: excellent performance (90-100), good performance (80-89), fair performance (70-79), needs improvement (60-69), poor performance (below 60), and missing/invalid assessment results.
2. Category-partition testing allows us to verify that appropriate feedback and grades are generated for each performance tier.
3. Pairwise testing adds overhead since there's essentially one configuration variable (score range). Catalogue-based testing is not necessary.

### g) The system must allow teachers to override automated feedback with manual feedback

**i. Level:** Since this requirement constrains the observable behaviour of the whole system for teacher feedback submission, which requires cooperation between teacher routes, authentication, and database updates, this is a system-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement can be partitioned into scenarios: teacher providing new feedback text only, teacher providing new grade only, teacher providing both feedback text and grade, teacher flagging recording for additional practice, and verifying the is_automated_feedback flag is set to false.
2. Category-partition testing ensures all combinations of teacher feedback updates are tested systematically.
3. Pairwise testing could be used here with feedback_text and grade as parameters, but category-partition testing is more explicit and easier to understand. Catalogue-based testing is not appropriate.

### h) The system must retrieve word data from external dictionary API and handle API failures gracefully

**i. Level:** Since this requirement constrains the observable behaviour of the whole system for word retrieval, which requires cooperation between word routes, dictionary service, external API calls, and error handling, this is a system-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement can be partitioned into scenarios: valid word found in dictionary, word not found in dictionary (404), dictionary API timeout, dictionary API returns malformed response, and word already exists in system database.
2. Category-partition testing allows systematic verification of both successful retrieval and proper error handling.
3. Pairwise testing is not suitable since these scenarios are independent error conditions. Catalogue-based testing would require a pre-existing catalogue of dictionary API failure modes.

### i) The system must correctly filter teacher submissions by status and class

**i. Level:** Since this requirement constrains the observable behaviour of the whole system for teacher dashboard functionality, which requires cooperation between teacher routes, database queries with multiple joins, and class management, this is a system-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional pairwise testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement has two independent configuration parameters: status filter (pending, reviewed, or none) and class filter (specific class ID or all classes). Pairwise testing allows us to efficiently test all combinations: (pending + specific class), (pending + all classes), (reviewed + specific class), (reviewed + all classes), (no filter + specific class), (no filter + all classes).
2. Pairwise testing is ideal here because the two filters are independent and we want to ensure they work correctly both individually and in combination.
3. Category-partition testing would work but would be essentially the same as pairwise in this case. Catalogue-based testing is not applicable.

### j) The system must calculate class analytics correctly including total recordings, pending reviews, average scores, most practiced words, and challenging words

**i. Level:** Since this requirement constrains the observable behaviour of the whole system for analytics calculation, which requires cooperation between teacher routes, complex database aggregations, and data formatting, this is a system-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Black-box testing

**iv. Appropriateness:**
1. This requirement involves verifying that aggregate calculations (counts, averages, rankings) are mathematically correct. A black-box test with known test data can verify that all analytics metrics match expected values.
2. We can create a test scenario with a controlled dataset where we know the exact values for total recordings, average scores, word practice counts, etc., and verify the system produces matching results.

### k) The system must generate a daily challenge word either from the database or from a predefined fallback list

**i. Level:** Since this requirement constrains the observable behaviour of the whole system for daily challenge word generation, which requires cooperation between word routes, database queries, and random selection logic, this is a system-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement can be partitioned into scenarios: database contains word assignments (should return one), database is empty (should return fallback word), dictionary API fails for database word (should try fallback), and dictionary API succeeds.
2. Category-partition testing allows us to verify the fallback mechanism works correctly when database is empty or when API calls fail.
3. Pairwise testing is not suitable since these are sequential fallback scenarios. Catalogue-based testing is not applicable.

### l) The system must return appropriate HTTP status codes for all API responses

**i. Level:** Since this requirement constrains the observable behaviour of the whole system across all endpoints, this is a system-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** System testing

**iv. Appropriateness:**
1. System testing is appropriate for verifying that the API consistently returns correct HTTP status codes (200 for success, 201 for creation, 400 for bad requests, 401 for unauthorized, 404 for not found, 500 for server errors) across all endpoints.
2. This is a global property that should be verified through systematic testing of all endpoints.

### m) The system must handle concurrent recording submissions from multiple students without data corruption

**i. Level:** Since this requirement constrains the observable behaviour of the whole system under concurrent load, which requires cooperation between API routes, database transactions, and file I/O, this is a system-level requirement.

**ii. Type:** Non-functional requirement (performance/reliability)

**iii. Testing approach:** System testing / Stress testing

**iv. Appropriateness:**
1. System testing and stress testing are appropriate for verifying concurrent operation. We can simulate multiple students submitting recordings simultaneously and verify that all recordings are saved correctly without data corruption or race conditions.
2. Stress testing specifically helps identify edge cases under high concurrent load that might not appear in normal usage.

## 2. Integration-level requirements

### a) When the submit_recording endpoint is called, the system must integrate pronunciation assessment service and feedback generation service correctly

**i. Level:** This requirement constrains how the recording submission endpoint interacts with both the pronunciation assessment service and the feedback generation service, which is clearly an integration-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Black-box testing

**iv. Appropriateness:**
1. This requirement is about ensuring the data flows correctly between services: audio file is passed to pronunciation service, assessment result is passed to feedback service, and final feedback is stored in the database.
2. A black-box integration test can verify that the complete flow works correctly by submitting a recording and checking that both automated scores and feedback are present in the response.

### b) When calculating student progress, the system must correctly aggregate data from recordings and student_progress tables

**i. Level:** This requirement constrains how the progress calculation logic interacts with multiple database tables and aggregation functions, which is an integration-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Black-box testing

**iv. Appropriateness:**
1. This requirement verifies that the integration between the API endpoint and database queries produces correct aggregate statistics.
2. A black-box test can create known test data in both tables and verify that the calculated progress matches expected values.

### c) The system must correctly integrate Azure Speech Service API with audio format conversion

**i. Level:** This requirement constrains how the pronunciation service interacts with the audio conversion utility before calling the Azure API, which is an integration-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement can be partitioned based on input audio format: already in correct format (16kHz, 16-bit, mono WAV), needs sample rate conversion, needs channel conversion (stereo to mono), needs bit depth conversion, and unsupported format.
2. Category-partition testing ensures the conversion logic correctly handles different input formats before Azure API call.
3. Pairwise testing could be used with three parameters (sample rate, bit depth, channels), but category-partition testing based on common input formats is more practical. Catalogue-based testing is not applicable.

### d) When a word is assigned by a teacher, the system must verify the word exists in the dictionary API before storing it

**i. Level:** This requirement constrains how the word assignment endpoint interacts with the dictionary service before database storage, which is an integration-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement can be partitioned into scenarios: word exists in dictionary and not in database (create new), word exists in both dictionary and database (update existing), word does not exist in dictionary (reject), and dictionary API fails (error handling).
2. Category-partition testing ensures proper integration between dictionary lookup and database operations.
3. Pairwise testing is not suitable since these scenarios are sequential decision points. Catalogue-based testing is not applicable.

### e) The system must correctly update both recording and word assignment records when a student submits a pronunciation recording

**i. Level:** This requirement constrains how the recording submission logic interacts with multiple database tables (recordings and word_assignments), which is an integration-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Black-box testing

**iv. Appropriateness:**
1. This requirement verifies that both tables are updated correctly in a single transaction: new recording is created and word practice count is incremented.
2. A black-box test can submit a recording and verify that both the recording exists and the word's times_practiced count has increased.

### f) The system must correctly join user and recording data when teachers retrieve student submissions

**i. Level:** This requirement constrains how the teacher submissions endpoint performs database joins between users and recordings tables, which is an integration-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Black-box testing

**iv. Appropriateness:**
1. This requirement verifies that the database join operation correctly associates student information with their recordings.
2. A black-box test can create test students and recordings, then verify that the submissions endpoint returns correctly matched data.

### g) The system must fall back to mock pronunciation assessment when Azure credentials are not configured

**i. Level:** This requirement constrains how the pronunciation service switches between Azure API and mock service based on configuration, which is an integration-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement can be partitioned into scenarios: Azure credentials configured and valid, Azure credentials not configured (use mock), Azure credentials configured but invalid (should fail gracefully), and Azure API call times out (error handling).
2. Category-partition testing ensures the fallback mechanism works correctly across different configuration states.
3. Pairwise testing is not suitable since these are alternative execution paths. Catalogue-based testing is not applicable.

### h) When updating student progress, the system must correctly calculate running average scores across multiple recordings

**i. Level:** This requirement constrains how the progress update logic integrates with existing progress records to maintain accurate averages, which is an integration-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Black-box testing

**iv. Appropriateness:**
1. This requirement verifies that the mathematical calculation for updating running averages is correct: (current_total * (attempts - 1) + new_score) / attempts.
2. A black-box test can create a progress record with known average and attempts, submit a new recording, and verify the updated average is correct.

### i) The system must correctly filter recordings by class membership through proper table joins

**i. Level:** This requirement constrains how the teacher analytics and submissions endpoints join recordings, class_enrollments, and classes tables, which is an integration-level requirement.

**ii. Type:** Functional requirement

**iii. Testing approach:** Black-box testing

**iv. Appropriateness:**
1. This requirement verifies that multi-table joins correctly filter recordings to only those from students enrolled in a specific class.
2. A black-box test can create classes with enrolled students, have them submit recordings, and verify that filtering by class returns only the correct recordings.

## 3. Unit-level requirements

### a) The _calculate_grade function should correctly convert numerical scores to letter grades

**i. Level:** This requirement governs the functionality of a single function in the FeedbackService, which means it is at the unit level.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement has clear partitions based on score ranges: A+ (95-100), A (90-94), A- (85-89), B+ (80-84), B (75-79), B- (70-74), C+ (65-69), C (60-64), C- (55-59), D (50-54), F (below 50).
2. Category-partition testing allows us to verify that each score range maps to the correct grade, including boundary conditions.
3. Pairwise testing is not applicable since there's only one input parameter. Catalogue-based testing is not necessary for this straightforward mapping.

### b) The _analyze_phonemes function should correctly identify problem phonemes with accuracy scores below 60

**i. Level:** This requirement governs the functionality of a single function in the FeedbackService, which means it is at the unit level.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement can be partitioned into scenarios: no phoneme data available, all phonemes have good scores (≥60), some phonemes have poor scores (<60), many phonemes have poor scores (should limit to first 3), and missing phoneme accuracy scores.
2. Category-partition testing ensures the function correctly handles different phoneme assessment patterns.
3. Pairwise testing is not suitable since these are different input data structures. Catalogue-based testing is not applicable.

### c) The enhance_feedback_with_teacher_notes function should correctly combine automated feedback with teacher notes

**i. Level:** This requirement governs the functionality of a single function in the FeedbackService, which means it is at the unit level.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement can be partitioned into scenarios: teacher notes provided (should combine), teacher notes empty (should return original), teacher notes contain only whitespace (should return original), and very long teacher notes (should handle gracefully).
2. Category-partition testing ensures correct behavior across different teacher note inputs.
3. Pairwise testing adds overhead since there's essentially one input parameter. Catalogue-based testing is not necessary.

### d) The verify_password function should correctly validate passwords against stored hashes

**i. Level:** This requirement governs the functionality of a single function in the security module, which means it is at the unit level.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement can be partitioned into scenarios: correct password (should return True), incorrect password (should return False), password with different case (should return False if case-sensitive), and special characters in password.
2. Category-partition testing ensures password verification works correctly across different input variations.
3. Pairwise testing is not applicable since there's only one logical input (password correctness). Catalogue-based testing is not necessary.

### e) The get_password_hash function should generate consistent hashes for the same password

**i. Level:** This requirement governs the functionality of a single function in the security module, which means it is at the unit level.

**ii. Type:** Functional requirement

**iii. Testing approach:** Black-box testing

**iv. Appropriateness:**
1. This requirement verifies that the same password can be verified against its hash, ensuring hash generation is consistent.
2. A simple black-box test that hashes a password and then verifies it should suffice.

### f) The create_access_token function should generate valid JWT tokens with correct claims

**i. Level:** This requirement governs the functionality of a single function in the security module, which means it is at the unit level.

**ii. Type:** Functional requirement

**iii. Testing approach:** Black-box testing

**iv. Appropriateness:**
1. This requirement verifies that JWT tokens contain the correct user ID claim and can be decoded and validated.
2. A black-box test that creates a token and decodes it to verify the claims is appropriate.

### g) The _convert_to_azure_format function should correctly convert audio files to Azure-compatible format

**i. Level:** This requirement governs the functionality of a single function in the PronunciationService, which means it is at the unit level.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement can be partitioned based on conversion needs: audio already in correct format (16kHz, mono, 16-bit), audio needs sample rate conversion, audio needs channel conversion, audio needs bit depth conversion, and audio in unsupported format.
2. Category-partition testing ensures the conversion function handles different input audio formats correctly.
3. Pairwise testing could be used with parameters (sample rate, channels, bit depth), but would generate too many test cases. Category-partition based on common formats is more practical. Catalogue-based testing is not applicable.

### h) The _get_mock_assessment function should generate realistic pronunciation scores within valid ranges

**i. Level:** This requirement governs the functionality of a single function in the PronunciationService, which means it is at the unit level.

**ii. Type:** Functional requirement

**iii. Testing approach:** Black-box testing

**iv. Appropriateness:**
1. This requirement verifies that mock scores fall within realistic ranges (typically 60-100 for pronunciation scores) and include all required fields.
2. A black-box test that calls the function multiple times and verifies score ranges and structure is appropriate.

### i) The generate_feedback function should include appropriate feedback components based on score ranges

**i. Level:** This requirement governs the functionality of a single function in the FeedbackService, which means it is at the unit level.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement can be partitioned based on score ranges: excellent (90-100), very good (80-89), good (70-79), fair (60-69), needs improvement (50-59), poor (below 50), and missing assessment data.
2. Category-partition testing ensures appropriate feedback text, tips, and encouragement are included for each performance tier.
3. Pairwise testing is not suitable since feedback generation depends primarily on the overall score. Catalogue-based testing is not applicable.

### j) The get_word_data function should correctly parse and format dictionary API responses

**i. Level:** This requirement governs the functionality of a single function in the DictionaryService, which means it is at the unit level.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement can be partitioned based on API response types: successful response with full data, successful response with minimal data, word not found (empty response), malformed JSON response, and network timeout.
2. Category-partition testing ensures the function correctly handles different API response scenarios.
3. Pairwise testing is not applicable since these are alternative response types. Catalogue-based testing could be useful if we had a catalogue of common dictionary API response patterns, but building such a catalogue would be excessive.

### k) The streak calculation logic should correctly count consecutive days of practice

**i. Level:** This requirement governs the functionality of streak calculation logic in the progress endpoint, which is a specific calculation unit.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement can be partitioned into scenarios: no practice history (streak = 0), practice today and yesterday (streak ≥ 2), practice today but not yesterday (streak = 1), gap in practice history (streak should stop at gap), and continuous daily practice for extended period.
2. Category-partition testing ensures the streak counting algorithm correctly handles different practice patterns.
3. Pairwise testing is not suitable since streak calculation depends on temporal sequences. Catalogue-based testing is not applicable.

### l) The password validation should enforce minimum password requirements

**i. Level:** This requirement governs the functionality of password validation logic, which is a specific validation unit.

**ii. Type:** Functional requirement

**iii. Testing approach:** Functional category-partition testing (black box, combinatorial)

**iv. Appropriateness:**
1. This requirement can be partitioned into scenarios: password meets all requirements, password too short, password contains only numbers, password contains only letters, empty password, and password with special characters.
2. Category-partition testing ensures password validation correctly accepts valid passwords and rejects invalid ones.
3. Pairwise testing could be used with parameters like (length, contains_numbers, contains_letters, contains_special_chars), but would generate many test cases. Category-partition based on common password patterns is more practical. Catalogue-based testing could use a catalogue of common weak passwords, but may be excessive for basic validation.
