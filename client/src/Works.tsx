import { useQuery, gql } from '@apollo/client';

const GET_WORKS = gql`
  query {
    allWorks {
      title
      year
      description
      genre
    }
  }
`;

export const Works = () => {
  const { loading, error, data } = useQuery(GET_WORKS);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error</p>;

  return (
    <div>
      {data.allWorks.map((work: any) => (
        <div key={work.title}>
          <h3>{work.title} ({work.year})</h3>
          <p>{work.description}</p>
          <small>{work.genre}</small>
        </div>
      ))}
    </div>
  );
};