import { ApolloClient, InMemoryCache } from "@apollo/client";

export const client = new ApolloClient({
    uri: 'http://backend:8000/graphql',
    cache: new InMemoryCache(),
  });