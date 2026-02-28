# Contributing Guidelines

Thank you for your interest in contributing to the ACH to RTP Conversion Service! This document outlines the process for contributing code, reporting issues, and suggesting improvements.

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. We are committed to providing a welcoming and inclusive environment for all participants.

## Getting Started

### Prerequisites

- Java 17+
- Maven 3.9+
- Git
- Docker & Docker Compose (for local development)
- PostgreSQL 15+ (or use docker-compose)
- RabbitMQ 3.12+ (or use docker-compose)

### Setting Up Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/ach-to-rtp-service.git
   cd ach-to-rtp-service
   ```

2. **Start dependencies**
   ```bash
   docker-compose up -d
   ```

3. **Build the project**
   ```bash
   mvn clean install
   ```

4. **Run the application**
   ```bash
   mvn spring-boot:run
   ```

5. **Verify setup**
   ```bash
   curl http://localhost:8080/api/v1/health/status
   ```

## Development Workflow

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

**Branch naming convention:**
- `feature/description`: New features
- `bugfix/description`: Bug fixes
- `docs/description`: Documentation updates
- `refactor/description`: Code refactoring
- `test/description`: Test improvements

### Making Changes

1. **Write code following project conventions**
   - Follow Java naming conventions
   - Use meaningful variable names
   - Add comments for complex logic
   - Keep methods focused and small

2. **Write tests for your changes**
   - Unit tests for new functionality
   - Integration tests for API changes
   - Aim for >80% code coverage
   - Test both success and failure paths

3. **Run tests locally**
   ```bash
   mvn clean test
   ```

4. **Check code quality**
   ```bash
   mvn checkstyle:check
   mvn spotbugs:check
   ```

### Committing Changes

**Commit message format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `chore`: Build, dependency, or tooling changes

**Example:**
```
feat: Add support for ACH file validation

- Implement comprehensive ACH record validation
- Add detailed error messages for validation failures
- Include validation tests

Closes #123
```

### Pushing Changes

```bash
git push origin feature/your-feature-name
```

## Pull Request Process

### Creating a Pull Request

1. **Push your branch to GitHub**
2. **Create a pull request** with a clear title and description
3. **Link related issues** using GitHub's issue linking
4. **Request reviewers** from the team

### PR Description Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation update
- [ ] Code refactoring

## Related Issues
Closes #123

## Testing
Describe how you tested the changes

## Checklist
- [ ] Code follows project style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] All tests pass locally
```

### Code Review

1. **Address feedback promptly**
2. **Request re-review** after making changes
3. **Resolve conflicts** if any
4. **Squash commits** before merging (if requested)

### Merging

- At least one approval required
- All CI checks must pass
- Branch must be up to date with main
- Use "Squash and merge" for clean history

## Coding Standards

### Java Style Guide

```java
// Class naming: PascalCase
public class AchFileParser {
    
    // Constant naming: UPPER_SNAKE_CASE
    private static final String RECORD_TYPE_FILE_HEADER = "1";
    
    // Method naming: camelCase
    public AchFile parseFile(InputStream inputStream, String fileName) {
        // Implementation
    }
    
    // Variable naming: camelCase
    int totalEntries = 0;
    
    // Add meaningful comments
    // Parse ACH file header record
    AchFileHeader header = parseFileHeader(record);
}
```

### Documentation Standards

```java
/**
 * Parse an ACH file from an input stream.
 * 
 * @param inputStream Input stream containing ACH file content
 * @param fileName Name of the file being parsed
 * @return Parsed AchFile object
 * @throws AchParsingException if parsing fails
 */
public AchFile parseFile(InputStream inputStream, String fileName) {
    // Implementation
}
```

### Test Naming Convention

```java
@Test
@DisplayName("Should extract string field correctly")
void testExtractStringField() {
    // Arrange
    String record = "test data";
    
    // Act
    String result = AchFieldExtractor.extractStringField(record, 1, 4);
    
    // Assert
    assertEquals("test", result);
}
```

## Testing Requirements

### Unit Tests

- Test all public methods
- Test both success and failure paths
- Use meaningful assertions
- Mock external dependencies

### Integration Tests

- Test component interactions
- Use test containers for databases
- Clean up test data after tests

### Test Coverage

- Minimum 80% code coverage
- Focus on critical paths
- Document coverage gaps

**Run coverage report:**
```bash
mvn clean test jacoco:report
open target/site/jacoco/index.html
```

## Documentation

### Code Comments

- Explain the "why", not the "what"
- Add comments for complex algorithms
- Keep comments up to date

### README Updates

- Update README.md for user-facing changes
- Add examples for new features
- Document breaking changes

### API Documentation

- Update API.md for endpoint changes
- Include request/response examples
- Document error responses

## Reporting Issues

### Bug Reports

**Title:** Brief description of the bug

**Description:**
```markdown
## Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Java version: 17
- OS: Linux/Mac/Windows
- Docker version: (if applicable)

## Logs
Relevant error logs or stack traces
```

### Feature Requests

**Title:** Brief description of the feature

**Description:**
```markdown
## Description
Clear description of the feature

## Motivation
Why is this feature needed?

## Proposed Solution
How should this feature work?

## Alternatives
Any alternative approaches?

## Additional Context
Any other relevant information
```

## Performance Considerations

When contributing code, consider:

1. **Efficiency**: Avoid unnecessary loops or operations
2. **Memory**: Be mindful of memory usage
3. **Database**: Optimize queries, use indexes
4. **Async**: Use async operations for I/O
5. **Caching**: Cache frequently accessed data

## Security Considerations

When contributing code, ensure:

1. **Input Validation**: Validate all inputs
2. **Error Handling**: Don't expose sensitive information
3. **Logging**: Don't log sensitive data
4. **Dependencies**: Keep dependencies up to date
5. **Secrets**: Never commit secrets or credentials

## Release Process

### Version Numbering

Follow semantic versioning: `MAJOR.MINOR.PATCH`

- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes

### Release Steps

1. Update version in `pom.xml`
2. Update `CHANGELOG.md`
3. Create release branch: `release/v1.0.0`
4. Create pull request
5. After merge, create GitHub release
6. Build and push Docker image

## Getting Help

- **Questions**: Open a discussion on GitHub
- **Bugs**: Open an issue with detailed information
- **Ideas**: Start a discussion or open an issue
- **Chat**: Join our Slack channel (if available)

## Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- GitHub contributors page

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project.

## Questions?

Feel free to reach out to the maintainers or open an issue for clarification.

Thank you for contributing! 🎉
