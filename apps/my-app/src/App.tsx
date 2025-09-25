import React, { useState } from "react";
import { Container, Form, Button, Row, Col, Card } from "react-bootstrap";

type Header = { key: string; value: string };

export default function App() {

  const [url, setUrl] = useState("");
  const [method, setMethod] = useState("GET");
  const [headers, setHeaders] = useState<Header[]>([{ key: "", value: "" }]);
  const [body, setBody] = useState("");
  const [response, setResponse] = useState<any>(null);

  const sendRequest = async () => {
    const headersObj: Record<string, string> = {};
    headers.forEach((h) => {
      if (h.key && h.value) headersObj[h.key] = h.value;
    });

    try {
      const res = await fetch(url, {
        method,
        headers: headersObj,
        body: ["GET", "HEAD"].includes(method) ? undefined : body,
        credentials: "include",
      });

      const text = await res.text();

      // Try to parse as JSON, fallback to text
      try {
        const json = JSON.parse(text);
        setResponse({
          status: res.status,
          statusText: res.statusText,
          headers: Object.fromEntries(res.headers.entries()),
          body: json,
        });
        return;
      } catch {}

      setResponse({
        status: res.status,
        statusText: res.statusText,
        headers: Object.fromEntries(res.headers.entries()),
        body: text,
      });
    } catch (err: any) {
      setResponse({ error: err.message });
    }
  };

  const handleHeaderChange = (
    i: number,
    field: "key" | "value",
    value: string
  ) => {
    const newHeaders = [...headers];
    newHeaders[i][field] = value;
    setHeaders(newHeaders);
  };

  return (
    <Container className="my-4">
      <h1 className="mb-4">HTTP Request Tester</h1>

      {/* URL & Method */}
      <Form.Group className="mb-3">
        <Form.Label>URL</Form.Label>
        <Form.Control
          type="text"
          placeholder="https://example.com/api"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label>Method</Form.Label>
        <Form.Select value={method} onChange={(e) => setMethod(e.target.value)}>
          {["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"].map(
            (m) => (
              <option key={m}>{m}</option>
            )
          )}
        </Form.Select>
      </Form.Group>

      {/* Headers */}
      <Card className="mb-3">
        <Card.Body>
          <Card.Title>Headers</Card.Title>
          {headers.map((h, i) => (
            <Row key={i} className="mb-2">
              <Col>
                <Form.Control
                  placeholder="Key"
                  value={h.key}
                  onChange={(e) => handleHeaderChange(i, "key", e.target.value)}
                />
              </Col>
              <Col>
                <Form.Control
                  placeholder="Value"
                  value={h.value}
                  onChange={(e) =>
                    handleHeaderChange(i, "value", e.target.value)
                  }
                />
              </Col>
            </Row>
          ))}
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setHeaders([...headers, { key: "", value: "" }])}
          >
            + Add Header
          </Button>
        </Card.Body>
      </Card>

      {/* Body */}
      {!["GET", "HEAD"].includes(method) && (
        <Form.Group className="mb-3">
          <Form.Label>Body</Form.Label>
          <Form.Control
            as="textarea"
            rows={5}
            value={body}
            onChange={(e) => setBody(e.target.value)}
          />
        </Form.Group>
      )}

      {/* Send */}
      <Button variant="primary" onClick={sendRequest}>
        Send Request
      </Button>

      {/* Response */}
      {response && (
        <Card className="mt-4">
          <Card.Body>
            <Card.Title>Response</Card.Title>
            <pre style={{ whiteSpace: "pre-wrap" }}>
              {JSON.stringify(response, null, 2)}
            </pre>
          </Card.Body>
        </Card>
      )}
    </Container>
  );
}
