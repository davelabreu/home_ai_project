import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useConfig } from '../../hooks/useConfig'; // Import useConfig

interface Message {
  text: string;
  sender: 'user' | 'ollama';
}

const ChatCard: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [isSending, setIsSending] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { monitor_target_host_set, monitorTargetHost, loading: configLoading } = useConfig();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    if (!monitorTargetHost) { // Should not happen if card is conditionally rendered, but as a safeguard
      setMessages((prev) => [...prev, { text: "Error: Remote host not configured for chat.", sender: "ollama" }]);
      return;
    }

    const newUserMessage: Message = { text: inputMessage, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, newUserMessage]);
    setInputMessage('');
    setIsSending(true);

    try {
      const chatApiUrl = `http://${monitorTargetHost}:5000/api/chat`; // Absolute URL
      const response = await fetch(chatApiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: inputMessage }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const ollamaResponse: Message = { text: data.response || data.error || 'Error: No response from Ollama', sender: 'ollama' };
      setMessages((prevMessages) => [...prevMessages, ollamaResponse]);
    } catch (error: any) {
      const errorMessage: Message = { text: `Error: ${error.message}`, sender: 'ollama' };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsSending(false);
    }
  };

  const isChatDisabled = !monitor_target_host_set || configLoading;

  return (
    <Card className="col-span-1 md:col-span-2 lg:col-span-1 h-[500px] flex flex-col">
      <CardHeader>
        <CardTitle>Chat with Jetson AI (Ollama)</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col space-y-4 overflow-hidden">
        <div className="flex-1 overflow-y-auto pr-4 -mr-4"> {/* Custom scrollbar handling */}
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex mb-2 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[70%] p-2 rounded-lg ${
                  msg.sender === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        {isChatDisabled && (
          <p className="text-center text-red-500 mt-2">
            Chat is only available when monitoring a remote host.
          </p>
        )}
        <div className="flex mt-auto space-x-2 p-2 border-t dark:border-gray-700">
          <Input
            type="text"
            placeholder="Type your message..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !isSending && !isChatDisabled) {
                handleSendMessage();
              }
            }}
            disabled={isSending || isChatDisabled}
            className="flex-1"
          />
          <Button onClick={handleSendMessage} disabled={isSending || isChatDisabled}>
            {isSending ? 'Sending...' : 'Send'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default ChatCard;
