# Test Greeting PIM

## Domain
test_greeting

## Version
1.0.0

## Description
A test greeting model for upload verification

## Entities

### TestMessage
- id: string (primary key)
- content: string (required)
- timestamp: datetime

## Services

### TestMessageService
- createMessage(content: string): TestMessage
- getMessage(id: string): TestMessage