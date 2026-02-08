import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useConfig } from '../hooks/useConfig'; // Corrected import path

interface Message {
  text: string;
  sender: 'user' | 'ollama';
}

const ChatCard: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [isSending, setIsSending] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { monitor_target_host_set, monitorTargetHost, monitorTargetPort, loading: configLoading, error: configError } = useConfig();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const newUserMessage: Message = { text: inputMessage, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, newUserMessage]);
    setInputMessage('');
    setIsSending(true);

    try {
      let chatApiUrl: string;
      if (monitor_target_host_set && monitorTargetHost && monitorTargetPort) {
        chatApiUrl = `http://${monitorTargetHost}:${monitorTargetPort}/api/chat`;
      } else {
        chatApiUrl = '/api/chat';
      }

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

  const isChatDisabled = isSending || configLoading;

  return (
    <Card className="col-span-1 md:col-span-2 lg:col-span-1 h-[400px] flex flex-col transition-all">
      <CardHeader className="py-3 px-4">
        <CardTitle className="text-sm font-semibold">Chat with AI (Ollama)</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col px-4 pb-3 space-y-3 overflow-hidden">
        <div className="flex-1 overflow-y-auto pr-2 -mr-2 space-y-2">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] px-3 py-1.5 rounded-2xl text-xs ${
                  msg.sender === 'user'
                    ? 'bg-primary text-primary-foreground rounded-tr-none'
                    : 'bg-muted text-foreground rounded-tl-none'
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        
        {configError && !monitor_target_host_set && (
          <p className="text-[10px] text-center text-destructive">
            Config Error: {configError}
          </p>
        )}
        
        <div className="flex items-center gap-2 pt-2 border-t border-border/50">
          <Input
            type="text"
            placeholder="Ask anything..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !isSending && !isChatDisabled) {
                handleSendMessage();
              }
            }}
            className="flex-1 h-8 text-xs px-3 focus-visible:ring-1"
          />
          <Button 
            onClick={handleSendMessage} 
            disabled={isChatDisabled}
            size="sm"
            className="h-8 px-3 text-xs"
          >
            {isSending ? '...' : 'Send'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default ChatCard;
